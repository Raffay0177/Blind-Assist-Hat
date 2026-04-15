#!/usr/bin/env python3
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

# Configuration & Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US")
OBSTACLE_WARN_DISTANCE_CM = int(os.getenv("OBSTACLE_WARN_DISTANCE_CM", "100"))

# Attempt OpenAI Import
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    print("WARN: openai package not installed.")
    client = None

# Attempt Camera Import
try:
    from picamera2 import Picamera2  # type: ignore
    csi_available = True
except ImportError:
    csi_available = False

# Attempt GPIO Import
try:
    import RPi.GPIO as GPIO  # type: ignore
    hardware_available = True
except ImportError:
    print("WARN: RPi.GPIO not found. Mocking globally for cross-platform testing.")
    from unittest.mock import MagicMock
    GPIO = MagicMock()
    sys.modules['RPi'] = MagicMock()
    sys.modules['RPi.GPIO'] = GPIO
    hardware_available = False

# GPIO Pin Mappings (BCM Numbering)
US_FRONT_TRIG = 23
US_FRONT_ECHO = 24
US_LEFT_TRIG = 5
US_LEFT_ECHO = 6
US_RIGHT_TRIG = 17
US_RIGHT_ECHO = 27

BTN_1_SCENE = 16
BTN_2_TEXT = 20
BTN_3_NAV = 21
BTN_4_REPEAT = 12

# ==========================================
# 1. STATE MANAGEMENT
# ==========================================

class AppState:
    def __init__(self):
        self.nav_mode_active = False
        self.last_output = ""
        self.is_speaking = False
        self.is_processing = False

    def toggle_nav_mode(self):
        self.nav_mode_active = not self.nav_mode_active
        return self.nav_mode_active

    def set_last_output(self, text):
        self.last_output = text

# Global singleton state
state = AppState()

# ==========================================
# 2. CAMERA MODULE
# ==========================================

def capture_image(filename="capture.jpg"):
    """
    Captures an image using the available camera hardware.
    Prioritizes CSI Camera (Picamera2), falls back to USB Camera (fswebcam).
    """
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    if csi_available:
        try:
            picam2 = Picamera2()
            picam2.configure(picam2.create_preview_configuration(main={"size": (1280, 720)}))
            picam2.start()
            time.sleep(1) # Let sensor adjust to lighting
            picam2.capture_file(filepath)
            picam2.stop()
            return filepath
        except Exception as e:
            print(f"DEBUG: CSI Camera (Picamera2) failed: {e}")

    if shutil.which("fswebcam"):
        try:
            print("📸 [USB CAMERA] Using fswebcam to capture.")
            subprocess.run(["fswebcam", "-r", "1280x720", "-S", "20", "--no-banner", filepath], check=True, capture_output=True)
            return filepath
        except Exception as e:
            print(f"DEBUG: USB Camera (fswebcam) failed: {e}")

    print("📸 [MOCK CAMERA] Click! Captured simulated image.")
    return "mocked_capture.jpg"

# ==========================================
# 3. AI & VISION ENGINE
# ==========================================

def encode_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(prompt_text, filename="captures/capture.jpg", force_high_accuracy=False):
    if not client:
        return f"Placeholder response for: {prompt_text}. OpenAI API key not configured yet."
        
    img_path = capture_image(filename)
    if not img_path:
        return "Failed to capture image from camera."
        
    if img_path == "mocked_capture.jpg":
        return f"Mocked vision analysis response for: {prompt_text}."
        
    base64_image = encode_image(img_path)
    
    try:
        model = "gpt-4o" if force_high_accuracy else "gpt-4o-mini"
        image_payload = {"url": f"data:image/jpeg;base64,{base64_image}"}
        if force_high_accuracy:
            image_payload["detail"] = "high"

        response = client.chat.completions.create(
          model=model,
          messages=[
            {
              "role": "user",
              "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": image_payload}
              ]
            }
          ],
          max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

def describe_scene():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captures/scene_{timestamp}.jpg"
    print(f"DEBUG: Saving Scene capture to {filename}")
    prompt = (
        "You are assisting a blind person via audio. Describe what the camera sees in 1-2 short sentences. "
        "Focus on: what objects are present, where they are, and any hazards or actions needed. "
        "Be direct and specific. No visual fluff."
    )
    return analyze_image(prompt, filename=filename)

def read_text():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captures/text_{timestamp}.jpg"
    print(f"DEBUG: Saving OCR capture to {filename}")
    return analyze_image(
        "I am a vision assistant for the blind. Please identify any text, signs, labels, or handwriting in this image. "
        "Read the text exactly as it appears. If multiple blocks of text exist, read them all clearly. "
        "If no text is visible, say 'No text detected'.", 
        filename=filename, force_high_accuracy=True
    )

def analyze_collision():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captures/collision_{timestamp}.jpg"
    print(f"DEBUG: Saving Collision capture to {filename}")
    prompt = (
        "A blind user is about to collide with an object straight ahead. "
        "Identify the object in 1-3 words, and give a very short instruction on how to avoid it. "
        "Example: 'Trash can. Step left.'"
    )
    return analyze_image(prompt, filename=filename, force_high_accuracy=False)

# ==========================================
# 4. TEXT TO SPEECH MODULE
# ==========================================

def speak(text):
    print(f"🔊 [TTS]: {text}")
    state.is_speaking = True
    
    if not client:
        _fallback_espeak(text)
        state.is_speaking = False
        return
        
    audio_file = "/tmp/speech_output.wav"
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", 
            input=text,
            response_format="wav" 
        )
        response.write_to_file(audio_file)
        subprocess.run(["aplay", "-q", audio_file], check=False)
        
    except Exception as e:
        print(f"DEBUG: OpenAI TTS Failed ({e}), falling back to espeak...")
        _fallback_espeak(text)
        
    state.is_speaking = False

def _fallback_espeak(text):
    text = text.replace(" ", "_").replace('"', "").replace("'", "")
    try:
        subprocess.run(("espeak \"" + text + "\" 2>/dev/null").split(" "), check=False)
    except FileNotFoundError:
        pass 

# ==========================================
# 5. NAVIGATION & AUDIO SYSTEMS
# ==========================================

def nav_setup():
    GPIO.setmode(GPIO.BCM) 
    sensors = [
        (US_FRONT_TRIG, US_FRONT_ECHO),
        (US_LEFT_TRIG, US_LEFT_ECHO),
        (US_RIGHT_TRIG, US_RIGHT_ECHO)
    ]
    for trig, echo in sensors:
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

def distance(trig_pin, echo_pin):
    GPIO.output(trig_pin, 0)
    time.sleep(0.000002)
    GPIO.output(trig_pin, 1)
    time.sleep(0.00001)
    GPIO.output(trig_pin, 0)

    start_time = time.time()
    end_time = time.time()

    timeout = start_time + 0.04 
    
    while GPIO.input(echo_pin) == 0 and time.time() < timeout:
        start_time = time.time()
    
    while GPIO.input(echo_pin) == 1 and time.time() < timeout:
        end_time = time.time()

    duration = end_time - start_time
    return (duration * 340 / 2) * 100  

# PyAudio setup
try:
    p = pyaudio.PyAudio()
except Exception:
    p = None

last_spoken_time = 0.0
last_direction = ""
last_vision_warning_time = 0.0

def collision_warning_routine():
    state.is_processing = True
    speak("Warning.")
    instruction = analyze_collision()
    speak(instruction)
    state.is_processing = False

def play_beep(duration_sec, frequency=800):
    if not p: return
    sample_rate = 44100
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
    tone = np.sin(frequency * t * 2 * np.pi)
    fade = min(int(sample_rate * 0.01), len(tone)//2)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)
    audio_data = (tone * 32767).astype(np.int16).tobytes()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()

def nav_loop():
    global last_spoken_time, last_direction, last_vision_warning_time
    
    while True:
        if not state.nav_mode_active:
            time.sleep(0.5)
            continue
            
        if state.is_speaking:
            time.sleep(0.1)
            continue
            
        dis_front = distance(US_FRONT_TRIG, US_FRONT_ECHO)
        dis_left = distance(US_LEFT_TRIG, US_LEFT_ECHO)
        dis_right = distance(US_RIGHT_TRIG, US_RIGHT_ECHO)

        min_distance = min(dis_front, dis_left, dis_right)
        
        if min_distance == dis_front: direction = "Front"
        elif min_distance == dis_left: direction = "Left"
        else: direction = "Right"

        print(f"Closest object: {min_distance:.1f} cm ({direction})", end="\r")

        if min_distance < OBSTACLE_WARN_DISTANCE_CM:
            current_time = time.time()
            if min_distance < 40:
                if direction == "Front" and current_time - last_vision_warning_time > 10.0 and not state.is_processing:
                    last_vision_warning_time = current_time
                    last_spoken_time = current_time
                    last_direction = direction
                    threading.Thread(target=collision_warning_routine, daemon=True).start()
                    time.sleep(0.1)
                    continue

                if current_time - last_spoken_time > 4.0 or direction != last_direction:
                    last_spoken_time = current_time
                    last_direction = direction
                    if not state.is_processing:
                        threading.Thread(target=speak, args=(f"{direction}",), daemon=True).start()
                        time.sleep(0.1) 
                    continue
        
        if direction == "Left": freq = 400
        elif direction == "Front": freq = 800
        else: freq = 1200

        if min_distance < 5:  
            play_beep(0.5, freq + 200) 
            time.sleep(0.1)
        elif min_distance < OBSTACLE_WARN_DISTANCE_CM:  
            beep_interval = (min_distance - 5) / 50.0  
            play_beep(0.1, freq)
            time.sleep(beep_interval)
        else:
            time.sleep(0.3)

def nav_destroy():
    if hardware_available:
        GPIO.cleanup()
    if p:
        p.terminate()

# ==========================================
# 6. BUTTON HANDLING & DISPATCHER
# ==========================================

# Keep global references to Button objects
_buttons = []

def setup_buttons(callback_fn):
    try:
        from gpiozero import Button
    except ImportError:
        print("DEBUG: gpiozero not installed. Physical buttons will not work.")
        return

    pins = [BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT]
    for pin in pins:
        try:
            btn = Button(pin, bounce_time=0.5)
            btn.when_pressed = lambda b=btn: callback_fn(b.pin.number)
            _buttons.append(btn)
        except Exception as e:
            print(f"DEBUG: Failed to initialize gpiozero Button on pin {pin}: {e}")

def handle_button_press(channel):
    if state.is_processing:
        print("\n[BLOCKED] Command ignored, system is already processing a request.")
        return
        
    if state.nav_mode_active and channel != BTN_3_NAV:
        print("\n[BLOCKED] User attempted to use another feature while Nav Mode is active.")
        speak("Please exit navigation mode first.")
        return

    if channel == BTN_1_SCENE:
        state.is_processing = True
        print("\n[Button 1] Describe Scene triggered.")
        threading.Thread(target=speak, args=("Looking straight ahead...",), daemon=True).start()
        text = describe_scene()
        state.set_last_output(text)
        speak(text)
        state.is_processing = False
        
    elif channel == BTN_2_TEXT:
        state.is_processing = True
        print("\n[Button 2] Read Text triggered.")
        threading.Thread(target=speak, args=("Scanning for text...",), daemon=True).start()
        text = read_text()
        state.set_last_output(text)
        speak(text)
        state.is_processing = False
        
    elif channel == BTN_3_NAV:
        print("\n[Button 3] Navigation Mode toggled.")
        is_active = state.toggle_nav_mode()
        if is_active:
            msg = "Sonar navigation systems online. Obstacle detection engaged."
        else:
            msg = "Navigation mode offline. Returning to standby."
        print(msg)
        speak(msg)
        
    elif channel == BTN_4_REPEAT:
        print("\n[Button 4] Repeat Last Output triggered.")
        if state.last_output:
            speak(state.last_output)
        else:
            speak("Nothing to repeat.")

# ==========================================
# 7. MAIN STARTUP LOGIC
# ==========================================

def main():
    print("Initializing Blind Assist Hat core system (Mono-file mode)...")
    
    if hardware_available:
        GPIO.setwarnings(False)
        GPIO.cleanup() 
    else:
        print("Running in MOCK mode.")
    
    # Setup Ultrasonics
    if hardware_available:
        nav_setup()
    
    # Setup Buttons
    try:
        setup_buttons(handle_button_press)
    except Exception as e:
        print(f"WARN: Could not setup buttons: {e}")
    
    # Start Navigation Thread
    nav_thread = threading.Thread(target=nav_loop, daemon=True)
    nav_thread.start()
    
    print("\n--- System Ready ---")
    print("Waiting for input. Press Ctrl+C to exit.")
    if not hardware_available:
        print("HINT: You can type 1, 2, 3, or 4 and press Enter to trigger features.")
        
    try:
        while True:
            user_input = input("Enter Command (1-4, or 'q' to quit): ").strip()
            
            if user_input == '1':
                handle_button_press(BTN_1_SCENE)
            elif user_input == '2':
                handle_button_press(BTN_2_TEXT)
            elif user_input == '3':
                handle_button_press(BTN_3_NAV)
            elif user_input == '4':
                handle_button_press(BTN_4_REPEAT)
            elif user_input.lower() == 'q':
                break
            else:
                if user_input:
                    print("Invalid input. Use 1, 2, 3, 4, or q.")
            
            time.sleep(0.1)
    except (KeyboardInterrupt, EOFError):
        print("\nShutting down system...")
        nav_destroy()

if __name__ == "__main__":
    main()
