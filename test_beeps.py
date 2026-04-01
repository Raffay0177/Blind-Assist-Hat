"""
test_beeps.py
Simulates the ultrasonic sensor beeping behaviour from navigation.py.
Walks through distance scenarios so you can hear exactly what the hat will sound like.
Run:  python test_beeps.py
"""

import time
import numpy as np

try:
    import pyaudio
except ImportError:
    print("[ERROR] pyaudio not installed. Run: pip install pyaudio")
    exit(1)

# ── Match the threshold from .env (default 100 cm) ────────────────────────
OBSTACLE_WARN_DISTANCE_CM = 100

# ── PyAudio setup ──────────────────────────────────────────────────────────
p = pyaudio.PyAudio()

def play_beep(duration_sec, frequency=800):
    """Generate and play a sine-wave beep (same code as navigation.py)."""
    sample_rate = 44100
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
    tone = np.sin(frequency * t * 2 * np.pi)

    # Smooth edges to prevent clicking/popping
    fade = min(int(sample_rate * 0.01), len(tone) // 2)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)

    audio_data = (tone * 29491).astype(np.int16).tobytes()  # ~90% volume
    stream = p.open(format=pyaudio.paInt16, channels=1,
                    rate=sample_rate, output=True)
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()

def simulate_distance(distance_cm, direction, label, steps=5):
    """
    Play beeps for a given simulated distance for a short demo period.
    Mirrors the exact logic from navigation.py loop().
    """
    print(f"\n{'─'*45}")
    print(f"  Simulating {direction}: {label} ({distance_cm} cm)")
    print(f"{'─'*45}")

    freq: int = 800
    if direction == "Left": freq = 400
    elif direction == "Front": freq = 800
    elif direction == "Right": freq = 1200
    
    spoken = False

    for i in range(steps):
        if distance_cm < OBSTACLE_WARN_DISTANCE_CM and not spoken:
            print(f"  🔊 [Voice Cue]: '{direction}'", flush=True)
            spoken = True
            time.sleep(1.0) # simulate time taken to speak
            
        if distance_cm < 5:
            # Very close: rapid continuous buzz, slightly higher pitch
            play_beep(0.5, freq + 200)
            print("  🚨 BUZZ!", flush=True)
            time.sleep(0.1)
        elif distance_cm < OBSTACLE_WARN_DISTANCE_CM:
            # Within warning zone: beep interval shrinks as distance shrinks
            beep_interval = max(0.1, (distance_cm - 5) / 50.0)
            play_beep(0.2, freq)  # longer beep for simulation
            print(f"  🔔 BEEP ({freq}Hz) (next in {beep_interval:.1f}s)", flush=True)
            time.sleep(beep_interval)
        else:
            # Safe: silence
            print("  (silent – object is far away)")
            time.sleep(0.3)
            break  # no need to repeat silence

# ── Demo Scenarios ─────────────────────────────────────────────────────────
print("=" * 45)
print("  Blind Assist Hat – Sensor Beep Simulator")
print("=" * 45)
print("Listen carefully — this is what you'll hear")
print("when obstacles are at different distances.\n")

scenarios = [
    (150, "Front", "Safe zone – no beep",          3),
    (90,  "Left",  "Far warning  (~90 cm)",         4),
    (55,  "Front", "Medium warning (~55 cm)",       4),
    (20,  "Right", "Close warning (~20 cm)",        4),
    (3,   "Front", "DANGER – object < 5 cm buzz",  5),
]

for dist, cur_dir, label, steps in scenarios:
    simulate_distance(dist, cur_dir, label, steps)
    time.sleep(0.5)  # brief pause between scenarios

print("\n\n[OK] Simulation complete.")
p.terminate()
