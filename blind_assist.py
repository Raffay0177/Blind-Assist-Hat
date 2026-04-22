#!/usr/bin/env python3
"""
Blind Assist Hat — Core Application
Runs on Raspberry Pi with HC-SR04 ultrasonic sensors, CSI/USB camera,
GPIO push-buttons, and OpenAI APIs for vision + TTS.
"""

import os
import sys
import time
import base64
import threading
import subprocess
import shutil
import datetime
import pyaudio
import numpy as np

# Try to import dotenv for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARN: python-dotenv not installed. Reading env vars directly.")

# ==========================================
# CONFIGURATION & ENVIRONMENT
# ==========================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# OpenAI TTS settings — voice options: alloy, echo, fable, onyx, nova, shimmer
# "nova" is warm and natural; "shimmer" is expressive and clear for guidance.
TTS_VOICE     = os.getenv("TTS_VOICE_NAME", "nova")          # OpenAI voice name
TTS_MODEL     = os.getenv("TTS_MODEL",      "tts-1-hd")      # tts-1 or tts-1-hd

# Navigation distance thresholds (cm)
# HC-SR04 reliable range: ~2 cm – 400 cm
# Tuned for typical indoor room environments (tighter than outdoor defaults)
ZONE_CRITICAL  = int(os.getenv("ZONE_CRITICAL_CM",  "40"))   # Imminent — stop now
ZONE_DANGER    = int(os.getenv("ZONE_DANGER_CM",    "90"))   # Very close — act now
ZONE_CAUTION   = int(os.getenv("ZONE_CAUTION_CM",  "160"))   # Approaching — heads up
ZONE_AWARE     = int(os.getenv("ZONE_AWARE_CM",    "280"))   # Environmental awareness

# Clear-path announcement cooldown (seconds)
# Increased to avoid spamming "path is clear" in open spaces
CLEAR_PATH_COOLDOWN = float(os.getenv("CLEAR_PATH_COOLDOWN", "12.0"))

# ==========================================
# OPENAI CLIENT
# ==========================================

try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    print("WARN: openai package not installed.")
    client = None

# ==========================================
# CAMERA
# ==========================================

try:
    from picamera2 import Picamera2  # type: ignore
    csi_available = True
except ImportError:
    csi_available = False

# ==========================================
# GPIO
# ==========================================

try:
    import RPi.GPIO as GPIO  # type: ignore
    hardware_available = True
except ImportError:
    print("WARN: RPi.GPIO not found — running in MOCK mode.")
    from unittest.mock import MagicMock
    GPIO = MagicMock()
    sys.modules['RPi']     = MagicMock()
    sys.modules['RPi.GPIO'] = GPIO
    hardware_available = False

# GPIO Pin Mappings (BCM Numbering) — must match .env and physical wiring
US_FRONT_TRIG = int(os.getenv("US_FRONT_TRIG", "23"))
US_FRONT_ECHO = int(os.getenv("US_FRONT_ECHO", "24"))
US_LEFT_TRIG  = int(os.getenv("US_LEFT_TRIG",  "5"))
US_LEFT_ECHO  = int(os.getenv("US_LEFT_ECHO",  "6"))
US_RIGHT_TRIG = int(os.getenv("US_RIGHT_TRIG", "17"))
US_RIGHT_ECHO = int(os.getenv("US_RIGHT_ECHO", "27"))

BTN_1_SCENE  = int(os.getenv("BTN_1_PIN", "16"))
BTN_2_TEXT   = int(os.getenv("BTN_2_PIN", "20"))
BTN_3_NAV    = int(os.getenv("BTN_3_PIN", "21"))
BTN_4_REPEAT = int(os.getenv("BTN_4_PIN", "12"))

# ==========================================
# 1. STATE MANAGEMENT
# ==========================================

class AppState:
    def __init__(self):
        self.nav_mode_active    = False
        self.last_output        = ""
        self.is_speaking        = False
        self.is_processing      = False

    def toggle_nav_mode(self):
        self.nav_mode_active = not self.nav_mode_active
        return self.nav_mode_active

    def set_last_output(self, text):
        self.last_output = text

state = AppState()

# ==========================================
# 2. CAMERA MODULE
# ==========================================

def capture_image(filename="capture.jpg"):
    """
    Captures an image:
    1. CSI Camera (Picamera2) — preferred
    2. USB Camera (fswebcam)  — fallback
    3. Mock                   — development fallback
    """
    capture_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures")
    os.makedirs(capture_dir, exist_ok=True)
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    if csi_available:
        try:
            picam2 = Picamera2()
            cfg = picam2.create_preview_configuration(main={"size": (1280, 720)})
            picam2.configure(cfg)
            picam2.start()
            time.sleep(1.0)   # sensor warm-up
            picam2.capture_file(filepath)
            picam2.stop()
            picam2.close()
            return filepath
        except Exception as e:
            print(f"DEBUG: CSI Camera (Picamera2) failed: {e}")

    if shutil.which("fswebcam"):
        try:
            print("📸 [USB CAMERA] Using fswebcam.")
            subprocess.run(
                ["fswebcam", "-r", "1280x720", "-S", "20", "--no-banner", filepath],
                check=True, capture_output=True
            )
            return filepath
        except Exception as e:
            print(f"DEBUG: USB Camera (fswebcam) failed: {e}")

    print("📸 [MOCK CAMERA] Simulated capture.")
    return "mocked_capture.jpg"

# ==========================================
# 3. AI & VISION ENGINE
# ==========================================

def encode_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_image(prompt_text, filename="captures/capture.jpg", force_high_accuracy=False):
    if not client:
        return f"[No API] Placeholder for: {prompt_text}"

    img_path = capture_image(filename)
    if not img_path:
        return "Failed to capture image."
    if img_path == "mocked_capture.jpg":
        return f"[Mock vision] {prompt_text}"

    base64_image = encode_image(img_path)
    if not base64_image:
        return "Failed to encode image."

    try:
        model   = "gpt-4o" if force_high_accuracy else "gpt-4o-mini"
        detail  = "high"   if force_high_accuracy else "auto"
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": detail}}
                ]
            }],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

def describe_scene():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return analyze_image(
        "You are assisting a blind person via audio. Describe what the camera sees in 1-2 short sentences. "
        "Focus on: what objects are present, where they are, and any immediate hazards. Be direct and specific.",
        filename=f"captures/scene_{ts}.jpg"
    )

def read_text():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return analyze_image(
        "I am a vision assistant for the blind. Identify any text, signs, labels, or handwriting in this image. "
        "Read the text exactly as it appears, left to right, top to bottom. If no text is visible, say 'No text detected'.",
        filename=f"captures/text_{ts}.jpg",
        force_high_accuracy=True
    )

def analyze_collision():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return analyze_image(
        "A blind user is about to collide with an object straight ahead. "
        "Identify the object in 1-3 words, and give one very short avoidance instruction. "
        "Example: 'Chair. Step right.'",
        filename=f"captures/collision_{ts}.jpg"
    )

# ==========================================
# 4. TEXT-TO-SPEECH  (OpenAI TTS-HD)
# ==========================================

_tts_lock = threading.Lock()

def speak(text):
    """
    Primary TTS: OpenAI tts-1-hd with natural voice (nova by default).
    Fallback: espeak for offline / no-API scenarios.
    Thread-safe via lock to prevent audio overlap.
    """
    if not text:
        return
    print(f"🔊 [TTS]: {text}")
    with _tts_lock:
        state.is_speaking = True
        if client:
            _openai_tts(text)
        else:
            _fallback_espeak(text)
        state.is_speaking = False

def _openai_tts(text):
    audio_file = "/tmp/bah_speech.mp3"
    try:
        response = client.audio.speech.create(
            model=TTS_MODEL,      # tts-1-hd for highest quality
            voice=TTS_VOICE,      # nova — warm, natural, clear for guidance
            input=text,
            response_format="mp3"
        )
        response.write_to_file(audio_file)
        # Use mpg123 if available (better mp3 support), else ffplay, else aplay with wav
        if shutil.which("mpg123"):
            subprocess.run(["mpg123", "-q", audio_file], check=False)
        elif shutil.which("ffplay"):
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_file], check=False)
        else:
            # Last resort: convert mp3 → wav and play with aplay
            wav_file = "/tmp/bah_speech.wav"
            subprocess.run(["ffmpeg", "-y", "-i", audio_file, wav_file], capture_output=True, check=False)
            subprocess.run(["aplay", "-q", wav_file], check=False)
    except Exception as e:
        print(f"DEBUG: OpenAI TTS failed ({e}), falling back to espeak.")
        _fallback_espeak(text)

def _fallback_espeak(text):
    """Offline TTS fallback using espeak."""
    try:
        clean = text.replace('"', '').replace("'", "")
        subprocess.run(["espeak", "-s", "140", clean], check=False, capture_output=True)
    except FileNotFoundError:
        print("WARN: espeak not found. No audio output.")

# ==========================================
# 5. NAVIGATION & AUDIO BEEP SYSTEM
# ==========================================

# PyAudio instance (shared)
try:
    _pa = pyaudio.PyAudio()
except Exception:
    _pa = None

def nav_setup():
    """Configure GPIO pins for all three HC-SR04 ultrasonic sensors."""
    GPIO.setmode(GPIO.BCM)
    for trig, echo in [
        (US_FRONT_TRIG, US_FRONT_ECHO),
        (US_LEFT_TRIG,  US_LEFT_ECHO),
        (US_RIGHT_TRIG, US_RIGHT_ECHO),
    ]:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

# HC-SR04 physically cannot detect closer than ~2 cm.
# Any reading below this is electrical noise — treat as invalid.
_MIN_VALID_CM = 2.0

def _read_distance(trig_pin, echo_pin, timeout_s=0.04):
    """
    Read distance from a single HC-SR04 sensor.
    Returns distance in centimetres, or 999 on timeout/error.

    FIX: TRIG is held LOW for 5µs (not 2µs) before pulsing — this fully
    resets the pin and prevents false triggers from residual charge.
    """
    try:
        # Hold TRIG LOW long enough to clear any residual signal
        GPIO.output(trig_pin, 0)
        time.sleep(0.000005)          # 5µs LOW — was 2µs, fixes false triggers
        GPIO.output(trig_pin, 1)
        time.sleep(0.00001)           # 10µs HIGH pulse to trigger sensor
        GPIO.output(trig_pin, 0)

        deadline = time.time() + timeout_s

        # Wait for ECHO to go HIGH (sensor detected pulse going out)
        while GPIO.input(echo_pin) == 0:
            if time.time() > deadline:
                return 999.0          # timeout = nothing detected
        t_start = time.time()

        # Wait for ECHO to go LOW (reflected pulse received back)
        while GPIO.input(echo_pin) == 1:
            if time.time() > deadline:
                return 999.0
        t_end = time.time()

        dist = (t_end - t_start) * 340 * 100 / 2  # speed of sound → cm

        # Reject physically impossible readings (noise / ringing artefact)
        if dist < _MIN_VALID_CM:
            return 999.0
        return dist
    except Exception:
        return 999.0

# Label used to identify sensor in terminal debug output
_SENSOR_LABELS = {}

def _read_distance_avg(trig_pin, echo_pin, samples=5, label=""):
    """
    Average multiple readings to reduce sensor noise.
    Drops the single highest AND lowest reading (trimmed mean) to
    reject both reflection spikes and false-short noise pulses.
    Prints every raw sample to terminal so you can see exactly what
    the sensor is reporting in real time.
    """
    readings = []
    raw_log = []
    for i in range(samples):
        d = _read_distance(trig_pin, echo_pin)
        raw = f"{d:6.1f}" if d < 999.0 else " NONE "
        raw_log.append(raw)
        if d < 999.0:
            readings.append(d)
        time.sleep(0.012)             # 12ms between samples — HC-SR04 settling time

    # Print every raw sample so you can see sensor behaviour live
    print(f"  [{label:5s}] raw: {' | '.join(raw_log)}")

    if not readings:
        return 999.0
    # Trimmed mean: drop highest AND lowest to filter outliers in both directions
    if len(readings) > 3:
        readings.remove(max(readings))
        readings.remove(min(readings))
    elif len(readings) > 2:
        readings.remove(max(readings))  # at least drop the high spike
    avg = sum(readings) / len(readings)
    print(f"  [{label:5s}] avg: {avg:6.1f} cm  zone={_zone_label(avg).upper()}")
    return avg

def _zone_label(dist_cm):
    """Return a human-readable proximity zone for a distance."""
    if dist_cm <= ZONE_CRITICAL:  return "critical"
    if dist_cm <= ZONE_DANGER:    return "danger"
    if dist_cm <= ZONE_CAUTION:   return "caution"
    if dist_cm <= ZONE_AWARE:     return "aware"
    return "clear"

def play_beep(duration_sec, frequency=800, volume=0.85):
    """Synthesise and play a short beep tone via PyAudio."""
    if not _pa:
        return
    sample_rate = 44100
    n = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n, False)
    tone = np.sin(frequency * t * 2 * np.pi) * volume
    # Smooth fade-in / fade-out to prevent clicks
    fade = min(int(sample_rate * 0.008), n // 2)
    tone[:fade]  *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)
    audio_data = (tone * 32767).astype(np.int16).tobytes()
    try:
        stream = _pa.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
    except Exception:
        pass

# ── Navigation state ──────────────────────────────────────────────────────────
_nav_last_spoken_time       = 0.0
_nav_last_direction         = ""
_nav_last_zone              = "clear"
_nav_last_clear_spoken_time = 0.0
_nav_last_vision_time       = 0.0

def _classify_scene(front, left, right):
    """
    Decide what voice cue (if any) to give based on all three sensor readings.
    Returns (message_or_None, beep_freq_or_None).
    Voice cues take priority over beeps.
    """
    f_zone = _zone_label(front)
    l_zone = _zone_label(left)
    r_zone = _zone_label(right)

    # Build a composite spoken warning
    warnings = []

    # Front sensor drives primary messaging
    if f_zone == "critical":
        warnings.append("Stop! Obstacle straight ahead")
    elif f_zone == "danger":
        warnings.append("Obstacle ahead")
    elif f_zone == "caution":
        warnings.append("Caution ahead")

    # Add side context if meaningful
    if l_zone in ("critical", "danger") and r_zone not in ("critical", "danger"):
        warnings.append("and to your left")
    elif r_zone in ("critical", "danger") and l_zone not in ("critical", "danger"):
        warnings.append("and to your right")
    elif l_zone in ("critical", "danger") and r_zone in ("critical", "danger"):
        warnings.append("on both sides")

    # If only side obstacles exist (front is clear)
    if not warnings:
        if l_zone in ("critical", "danger"):
            warnings.append("Obstacle on your left")
        if r_zone in ("critical", "danger"):
            warnings.append("Obstacle on your right")

    # Compose message
    message = " ".join(warnings) + ("." if warnings else "")

    # Determine beep frequency to accompany or replace voice
    # Lower pitch = left, Mid = front, Higher = right
    min_dist = min(front, left, right)
    if min_dist == left:
        freq = 450
    elif min_dist == front:
        freq = 850
    else:
        freq = 1200

    return (message if warnings else None), freq, min_dist

def collision_warning_routine():
    """
    Triggered on imminent/critical front obstacle.
    AUTO SCENE DESCRIBE DISABLED — camera AI analysis removed because:
      - It adds 1-3s latency at the worst possible moment
      - The user needs an instant reaction, not a wait
      - Use Button 1 manually to get a scene description instead
    Now just fires an immediate urgent voice warning.
    """
    state.is_processing = True
    speak("Stop! Obstacle directly ahead.")
    state.is_processing = False

def nav_loop():
    """
    Main navigation loop — runs in a background thread.
    
    Zone behaviour:
    ┌──────────────────┬────────────────────────────────────────────────────┐
    │ Zone             │ Feedback                                            │
    ├──────────────────┼────────────────────────────────────────────────────┤
    │ clear   >350cm   │ Occasional "Path is clear" message                  │
    │ aware   ≤350cm   │ Slow beeps (every ~1.5 s)                           │
    │ caution ≤200cm   │ Faster beeps + voice if direction changed           │
    │ danger  ≤120cm   │ Rapid beeps + voice warning (every 4 s)            │
    │ critical ≤50cm   │ Continuous fast beeps + voice + camera analysis    │
    └──────────────────┴────────────────────────────────────────────────────┘
    """
    global _nav_last_spoken_time, _nav_last_direction, _nav_last_zone
    global _nav_last_clear_spoken_time, _nav_last_vision_time

    while True:
        if not state.nav_mode_active:
            time.sleep(0.5)
            continue

        if state.is_processing:
            time.sleep(0.2)
            continue

        # --- Read sensors ---
        # CRITICAL: Fire each sensor sequentially with a 60ms gap.
        # HC-SR04 operates at 40kHz ultrasound — if two sensors fire within
        # ~30ms of each other, the second sensor picks up the first sensor's
        # reflected echo as its own return pulse, causing totally wrong readings.
        # 60ms gap ensures the ultrasonic burst from one sensor has fully
        # dissipated before the next sensor fires.
        print("  ─── Sensor Sweep ─────────────────────────────")
        front = _read_distance_avg(US_FRONT_TRIG, US_FRONT_ECHO, label="FRONT")
        time.sleep(0.10)              # 100ms gap — ensures front pulse fully dissipates
        left  = _read_distance_avg(US_LEFT_TRIG,  US_LEFT_ECHO,  label="LEFT ")
        time.sleep(0.10)              # 100ms gap
        right = _read_distance_avg(US_RIGHT_TRIG, US_RIGHT_ECHO, label="RIGHT")

        now = time.time()
        min_dist = min(front, left, right)
        overall_zone = _zone_label(min_dist)

        # Determine closest direction — use explicit <= comparisons, NOT ==
        # Float equality (==) is unreliable and was causing wrong direction picks
        if front <= left and front <= right:
            direction = "Front"
        elif left <= right:
            direction = "Left"
        else:
            direction = "Right"

        print(
            f"  ──> SUMMARY | F:{front:6.1f}cm  L:{left:6.1f}cm  R:{right:6.1f}cm"
            f"  →  {direction} is closest  ({overall_zone.upper()})"
        )

        # ── CLEAR PATH ───────────────────────────────────────────────────────
        if overall_zone == "clear":
            if now - _nav_last_clear_spoken_time > CLEAR_PATH_COOLDOWN:
                _nav_last_clear_spoken_time = now
                _nav_last_zone = "clear"
                threading.Thread(
                    target=speak, args=("Path is clear.",), daemon=True
                ).start()
            time.sleep(0.5)
            continue

        # ── COMPUTE WARNINGS ─────────────────────────────────────────────────
        voice_msg, beep_freq, _ = _classify_scene(front, left, right)

        # ── CRITICAL: imminent collision with camera analysis ─────────────────
        if overall_zone == "critical" and direction == "Front":
            if now - _nav_last_vision_time > 10.0:
                _nav_last_vision_time = now
                _nav_last_spoken_time = now
                threading.Thread(target=collision_warning_routine, daemon=True).start()
                # Fast beep while processing
                play_beep(0.05, beep_freq + 300)
                time.sleep(0.1)
                continue

        # ── VOICE CUE (danger/critical interval or direction changed) ─────────
        direction_changed = (direction != _nav_last_direction)
        zone_worsened     = (
            _nav_last_zone in ("clear", "aware", "caution") and
            overall_zone in ("danger", "critical")
        )

        # Voice cooldowns by zone (how many seconds to wait before repeating)
        # Shorter = more frequent alerts; tuned so it's informative not annoying
        voice_cooldown = {
            "critical": 2.5,    # repeat every 2.5s when about to hit something
            "danger":   5.0,    # repeat every 5s when close
            "caution":  8.0,    # repeat every 8s when approaching
            "aware":    999.0,  # beeps only; no voice for far-awareness zone
        }.get(overall_zone, 6.0)

        if voice_msg and not state.is_speaking:
            if direction_changed or zone_worsened or (now - _nav_last_spoken_time > voice_cooldown):
                _nav_last_spoken_time = now
                _nav_last_direction   = direction
                _nav_last_zone        = overall_zone
                threading.Thread(target=speak, args=(voice_msg,), daemon=True).start()
                time.sleep(0.15)
                continue

        _nav_last_direction = direction
        _nav_last_zone      = overall_zone

        # ── BEEP FEEDBACK (rate scales with proximity) ─────────────────────────
        # Beep interval: 0.08 s (critical) → 1.2 s (aware boundary)
        # Tightened upper bound for quicker awareness feedback indoors
        clamped = max(5.0, min(min_dist, float(ZONE_AWARE)))
        t_range  = float(ZONE_AWARE) - 5.0
        beep_interval = 0.08 + (clamped - 5.0) / t_range * 1.12   # 0.08 → 1.2 s
        beep_dur  = max(0.05, 0.18 - (clamped / float(ZONE_AWARE)) * 0.13)

        play_beep(beep_dur, beep_freq)
        time.sleep(beep_interval)

def nav_destroy():
    if hardware_available:
        GPIO.cleanup()
    if _pa:
        _pa.terminate()

# ==========================================
# 6. BUTTON HANDLING & DISPATCHER
# ==========================================

_buttons = []  # keep gpiozero Button objects alive

def setup_buttons(callback_fn):
    try:
        from gpiozero import Button
    except ImportError:
        print("DEBUG: gpiozero not installed. Physical buttons disabled.")
        return

    for pin in [BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT]:
        try:
            btn = Button(pin, bounce_time=0.05)
            btn.when_pressed = lambda b=btn: callback_fn(b.pin.number)
            _buttons.append(btn)
            print(f"  ✓ Button registered on GPIO {pin}")
        except Exception as e:
            print(f"  ✗ Button GPIO {pin} failed: {e}")

def handle_button_press(channel):
    if state.is_processing:
        print("\n[BLOCKED] System already processing.")
        return

    if state.nav_mode_active and channel != BTN_3_NAV:
        print("\n[BLOCKED] Exit navigation mode first.")
        speak("Please exit navigation mode first.")
        return

    if channel == BTN_1_SCENE:
        state.is_processing = True
        print("\n[Button 1] Describe Scene.")
        speak("Looking around…")
        text = describe_scene()
        state.set_last_output(text)
        speak(text)
        state.is_processing = False

    elif channel == BTN_2_TEXT:
        state.is_processing = True
        print("\n[Button 2] Read Text.")
        speak("Scanning for text…")
        text = read_text()
        state.set_last_output(text)
        speak(text)
        state.is_processing = False

    elif channel == BTN_3_NAV:
        print("\n[Button 3] Toggle Navigation Mode.")
        is_active = state.toggle_nav_mode()
        if is_active:
            msg = "Navigation mode active. I will guide you with audio."
        else:
            msg = "Navigation mode off."
        speak(msg)

    elif channel == BTN_4_REPEAT:
        print("\n[Button 4] Repeat Last Output.")
        speak(state.last_output if state.last_output else "Nothing to repeat.")

# ==========================================
# 7. MAIN STARTUP
# ==========================================

def main():
    print("=" * 50)
    print("  Blind Assist Hat — System Starting")
    print("=" * 50)
    print(f"  TTS   : {TTS_MODEL} / voice={TTS_VOICE}")
    print(f"  API   : {'✓ OpenAI connected' if client else '✗ No API key — mock mode'}")
    print(f"  HW    : {'✓ RPi GPIO available' if hardware_available else '✗ Mock mode'}")
    print(f"  Camera: {'✓ CSI (Picamera2)' if csi_available else '✗ USB / mock'}")
    print(f"  Zones : Critical≤{ZONE_CRITICAL}cm / Danger≤{ZONE_DANGER}cm / Caution≤{ZONE_CAUTION}cm / Aware≤{ZONE_AWARE}cm")
    print("=" * 50)

    if hardware_available:
        GPIO.setwarnings(False)
        GPIO.cleanup()
        nav_setup()

    try:
        setup_buttons(handle_button_press)
    except Exception as e:
        print(f"WARN: Button setup failed: {e}")

    nav_thread = threading.Thread(target=nav_loop, daemon=True)
    nav_thread.start()

    speak("Blind Assist Hat ready.")

    print("\n--- System Ready ---")
    print("Controls: 1=Scene  2=Text  3=Nav  4=Repeat  q=Quit")
    if not hardware_available:
        print("(Running in mock mode — type commands above and press Enter)")

    try:
        while True:
            user_input = input("> ").strip()
            if   user_input == "1": handle_button_press(BTN_1_SCENE)
            elif user_input == "2": handle_button_press(BTN_2_TEXT)
            elif user_input == "3": handle_button_press(BTN_3_NAV)
            elif user_input == "4": handle_button_press(BTN_4_REPEAT)
            elif user_input.lower() in ("q", "quit", "exit"):
                break
            elif user_input:
                print("  Use 1 / 2 / 3 / 4 / q")
            time.sleep(0.05)
    except (KeyboardInterrupt, EOFError):
        print("\n\nShutting down…")
    finally:
        nav_destroy()
        print("Goodbye.")

if __name__ == "__main__":
    main()
