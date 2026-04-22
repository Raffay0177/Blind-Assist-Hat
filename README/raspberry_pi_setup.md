# 🍓 Raspberry Pi Complete Setup Guide

Follow this step-by-step guide to get the Blind Assist Hat running from scratch on a new Raspberry Pi.

## 1. Hardware Preparation
Before turning on the Raspberry Pi, ensure all physical components are connected correctly.
- **Camera:** Connect the ribbon cable to the CSI port.
- **Speaker:** Plug your speaker or headphones into the 3.5mm audio jack.
- **Ultrasonic Sensors & Buttons:** Carefully wire these to the GPIO pins. 
  > ⚠️ **CRITICAL:** Ensure you use a voltage divider on the Ultrasonic *Echo* pins so you don't send 5V into the Pi's 3.3V GPIO pins! 
  *(Detailed pin map: `hardware/schematics/gpio_wiring.md`)*

## 2. Raspberry Pi OS Setup
1. Use the **Raspberry Pi Imager** to flash an SD card with **Raspberry Pi OS (64-bit)**.
2. Ensure you enable Wi-Fi and SSH in the advanced settings of the imager so it automatically connects to your network.
3. Insert the SD card, power on the Pi, and either connect it to a monitor/keyboard or SSH into it from your computer.

## 3. Clone the Project
Open the Raspberry Pi's terminal and download the code from your GitHub repository:
```bash
git clone https://github.com/Raffay0177/Blind-Assist-Hat.git
cd Blind-Assist-Hat
```

## 4. Run the Automated Installer
The repository includes a script that automatically updates your system and installs all necessary dependencies (like `espeak`, `picamera2`, `openai`, and `Python Virtual Environments`).

Run this command:
```bash
bash install.sh
```
*(This may take a few minutes depending on your internet connection).*

## 5. Configure Your Keys
The AI Vision mapping requires an OpenAI API key.

1. Once the installer finishes, copy the template `.env` file to create your local copy:
   ```bash
   cp .env.example .env
   ```
2. Open the file to edit it:
   ```bash
   nano .env
   ```
3. Find the line `OPENAI_API_KEY=...` and replace the placeholder with your actual OpenAI key.
4. Save and exit (Press `Ctrl+O`, hit `Enter`, then press `Ctrl+X`).

## 6. Run the Software!
Activate your virtual environment (where the installer put all the Python libraries) and boot up the core system:
```bash
source venv/bin/activate
python -m core.main
```

You should hear the script launch, and the system is now ready to respond to your wrist button presses! 🎉
