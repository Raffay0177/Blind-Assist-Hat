#!/bin/bash
# One-shot setup script for Raspberry Pi

echo "Setting up Blind Assist Hat dependencies..."

# System dependencies
sudo apt-get update
sudo apt-get install -y espeak python3-pip python3-venv sox libportaudio2 fswebcam

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

echo "Setup complete. Please enter your API keys inside the .env file."
echo "To run: source venv/bin/activate && python core/main.py"
