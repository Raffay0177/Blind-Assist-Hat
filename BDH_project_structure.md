# BDH — Blind Aid Device (Hardware) Project Structure

```
BDH/
├── .env                          # Environment variables (see template below)
├── .env.example                  # Committed version with placeholder values
├── .gitignore                    # Ignores .env, __pycache__, logs, etc.
├── README.md                     # Project overview & setup guide
│
├── hardware/
│   ├── schematics/
│   │   ├── gpio_wiring.md        # Pi GPIO pin assignments for all sensors
│   │   ├── voltage_divider.md    # HC-SR04 5V → 3.3V divider diagram
│   │   └── wrist_pad_wiring.md   # 4-button fan pad GPIO wiring
│   │
│   └── 3d_models/
│       ├── wrist_mount_base.scad # OpenSCAD: wrist sleeve base
│       ├── fan_arm.scad          # OpenSCAD: single fan arm (print x4)
│       └── glasses_sensor_clip.scad
│
├── config/
│   ├── settings.py               # Loads .env vars via python-dotenv
│   └── gpio_map.py               # Centralized GPIO pin constants
│
├── sensors/
│   ├── __init__.py
│   ├── ultrasonic.py             # HC-SR04 driver (front, left, right)
│   └── camera.py                 # Pi Camera module wrapper
│
├── input/
│   ├── __init__.py
│   └── wrist_buttons.py          # GPIO interrupt callbacks for 4-button pad
│                                 # B1: Describe scene | B2: Read text/signs
│                                 # B3: Navigation mode | B4: Repeat last output
│
├── ai/
│   ├── __init__.py
│   ├── vision.py                 # Calls vision API (describe scene / read text)
│   ├── navigation.py             # Obstacle proximity logic + TTS directions
│   └── tts.py                    # Text-to-speech output handler
│
├── core/
│   ├── __init__.py
│   ├── main.py                   # Entry point — starts all threads/loops
│   ├── state.py                  # Global device state (current mode, last output)
│   └── dispatcher.py             # Routes button presses to correct AI module
│
├── logs/
│   └── .gitkeep                  # Log files written here at runtime
│
├── tests/
│   ├── test_ultrasonic.py
│   ├── test_buttons.py
│   └── test_vision.py
│
├── requirements.txt              # Python dependencies
└── install.sh                    # One-shot setup script for Pi
```

---

## .env Template (copy to .env and fill in)

```env
# ─── AI / API Keys ─────────────────────────────────────────────
OPENAI_API_KEY=your_openai_key_here          # Used for vision (GPT-4o)
# or if using Google Gemini:
GEMINI_API_KEY=your_gemini_key_here

# ─── GPIO Pin Assignments ──────────────────────────────────────
# Ultrasonic Sensors (HC-SR04)
US_FRONT_TRIG=23
US_FRONT_ECHO=24
US_LEFT_TRIG=17
US_LEFT_ECHO=27
US_RIGHT_TRIG=5
US_RIGHT_ECHO=6

# Wrist Button Pad
BTN_1_PIN=16   # Describe scene
BTN_2_PIN=20   # Read text / signs
BTN_3_PIN=21   # Navigation mode
BTN_4_PIN=12   # Repeat last output

# ─── Device Settings ───────────────────────────────────────────
OBSTACLE_WARN_DISTANCE_CM=100    # Alert when object closer than this
TTS_VOICE=en-US                  # TTS voice/language
TTS_SPEED=1.0                    # 1.0 = normal speed
LOG_LEVEL=INFO                   # DEBUG | INFO | WARNING | ERROR

# ─── Camera ────────────────────────────────────────────────────
CAMERA_RESOLUTION=1280x720
CAMERA_FRAMERATE=30
```

---

## .env.example (commit this, NOT .env)

```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
US_FRONT_TRIG=23
US_FRONT_ECHO=24
US_LEFT_TRIG=17
US_LEFT_ECHO=27
US_RIGHT_TRIG=5
US_RIGHT_ECHO=6
BTN_1_PIN=16
BTN_2_PIN=20
BTN_3_PIN=21
BTN_4_PIN=12
OBSTACLE_WARN_DISTANCE_CM=100
TTS_VOICE=en-US
TTS_SPEED=1.0
LOG_LEVEL=INFO
CAMERA_RESOLUTION=1280x720
CAMERA_FRAMERATE=30
```

---

## requirements.txt

```
RPi.GPIO>=0.7.1
picamera2>=0.3.12
openai>=1.0.0
gTTS>=2.3.2
playsound>=1.3.0
python-dotenv>=1.0.0
numpy>=1.24.0
Pillow>=10.0.0
```

---

## .gitignore

```
.env
__pycache__/
*.pyc
logs/*.log
*.egg-info/
.DS_Store
```
