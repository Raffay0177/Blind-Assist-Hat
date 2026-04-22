# 🧢 Blind Assist Hat (BAH)

Welcome to the **Blind Assist Hat** project! This project aims to create an affordable, smart wearable device designed to help visually impaired individuals navigate their surroundings, read text, and understand the environment around them.

The system uses a combination of ultrasonic sensors, a Raspberry Pi Camera, and OpenAI's GPT-4o Vision API to act as a pair of "digital eyes," controlled entirely via a tactile 4-button wrist pad.

---

## 🌟 Key Features

1. **Obstacle Detection:** Ultrasonic sensors on the front, left, and right gently warn the user via dynamic audio beeps if they are getting too close to an object.
2. **Scene Description:** The AI looks through the camera and verbally describes what is in front of the user (e.g., *"There is a park bench and a tree ahead."*).
3. **Text Reading:** Identifies and reads street signs, documents, or labels out loud.
4. **Navigation Mode:** Toggles continuous proximity sensing.

---

## 🛠️ System Architecture

### 1. The 'Brain' (Raspberry Pi)
A Raspberry Pi acts as the central hub, processing all hardware interrupts and routing API calls.

### 2. The 'Eyes' (Sensors & Camera)
- **Camera (CSI Port):** Captures high-res frames for the Vision AI.
- **Ultrasonics (HC-SR04):** Measures physical distances. *(Warning: Requires a voltage divider for the Echo pins to protect the Pi's 3.3V GPIO).*

### 3. The 'Remote' (Wrist Pad)
A 4-button tactile interface worn on the wrist:
- **Button 1:** Describe the scene.
- **Button 2:** Read text/signs.
- **Button 3:** Toggle Navigation Mode (Ultrasonic warnings).
- **Button 4:** Repeat the last spoken output.

### 4. The 'Voice' (Speaker)
Native synthesized speech (Text-to-Speech) pushed directly through the Pi's 3.5mm Jack or HDMI port. No external buzzer required!

---

## 📁 Project Structure

```text
BDH/
├── ai/                 # OpenAI Vision API routing and TTS handlers
├── config/             # Centralized settings and GPIO pin mappings
├── core/               # Main application loop, state handling, and button dispatchers
├── hardware/           # Hardware schematics, 3D printable STL/SCAD models
├── input/              # GPIO button interrupt logic
├── sensors/            # Ultrasonic distance algorithms and picamera2 wrappers
├── tests/              # End-to-end workflow suite for PC testing
├── .env.example        # Environment variable template
├── install.sh          # One-shot Raspberry Pi setup script
└── requirements.txt    # Current Python dependencies
```

---

## 🚀 Getting Started

If you are a builder or technician setting this up on a Raspberry Pi, follow these steps:

### 1. Hardware Assembly
Before booting, refer to the wiring guides in the `hardware/schematics/` folder. 
> **Important:** Follow `hardware/schematics/gpio_wiring.md` closely to ensure you don't fry your Raspberry Pi using the 5V ultrasonic sensors!

### 2. Software Installation
Run the one-shot setup script to install all system dependencies (like `espeak` and `libcamera`) and generate the Python virtual environment:
```bash
bash install.sh
```

### 3. Configuration
Copy the provided `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure your API keys:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OBSTACLE_WARN_DISTANCE_CM=100
```
*(You can also adjust the max warning distance for ultrasonic navigation mode here).*

### 4. Running the System
Activate your environment and start the core loop:
```bash
source venv/bin/activate
python -m core.main
```

---

## 💻 Cross-Platform Testing (Windows/Mac)
Don't have a Raspberry Pi handy? The codebase is designed to safely degrade when missing physical hardware.
You can run `python tests/test_end_to_end.py` on your Windows/Mac PC to simulate button presses and test the flow logs!
