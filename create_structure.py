import os

base_dir = r"c:\Users\raffa\OneDrive\Documents\FSE\BAH"

files = {
    ".env": """# ─── AI / API Keys ─────────────────────────────────────────────
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
""",
    ".env.example": """OPENAI_API_KEY=sk-...
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
""",
    ".gitignore": """.env
__pycache__/
*.pyc
logs/*.log
*.egg-info/
.DS_Store
""",
    "requirements.txt": """RPi.GPIO>=0.7.1
picamera2>=0.3.12
openai>=1.0.0
gTTS>=2.3.2
playsound>=1.3.0
python-dotenv>=1.0.0
numpy>=1.24.0
Pillow>=10.0.0
""",
    "README.md": "# Blind Assist Hat\n\nProject overview & setup guide.\n",
    "hardware/schematics/gpio_wiring.md": "# Pi GPIO pin assignments for all sensors\n",
    "hardware/schematics/voltage_divider.md": "# HC-SR04 5V → 3.3V divider diagram\n",
    "hardware/schematics/wrist_pad_wiring.md": "# 4-button fan pad GPIO wiring\n",
    "hardware/3d_models/wrist_mount_base.scad": "// OpenSCAD: wrist sleeve base\n",
    "hardware/3d_models/fan_arm.scad": "// OpenSCAD: single fan arm (print x4)\n",
    "hardware/3d_models/glasses_sensor_clip.scad": "// OpenSCAD: glasses sensor clip\n",
    "config/settings.py": "# Loads .env vars via python-dotenv\n",
    "config/gpio_map.py": "# Centralized GPIO pin constants\n",
    "sensors/__init__.py": "",
    "sensors/ultrasonic.py": "# HC-SR04 driver (front, left, right)\n",
    "sensors/camera.py": "# Pi Camera module wrapper\n",
    "input/__init__.py": "",
    "input/wrist_buttons.py": "# GPIO interrupt callbacks for 4-button pad\n",
    "ai/__init__.py": "",
    "ai/vision.py": "# Calls vision API (describe scene / read text)\n",
    "ai/navigation.py": "# Obstacle proximity logic + TTS directions\n",
    "ai/tts.py": "# Text-to-speech output handler\n",
    "core/__init__.py": "",
    "core/main.py": "# Entry point — starts all threads/loops\n",
    "core/state.py": "# Global device state (current mode, last output)\n",
    "core/dispatcher.py": "# Routes button presses to correct AI module\n",
    "logs/.gitkeep": "",
    "tests/test_ultrasonic.py": "",
    "tests/test_buttons.py": "",
    "tests/test_vision.py": "",
    "install.sh": "# One-shot setup script for Pi\n"
}

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files created successfully.")
