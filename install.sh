#!/bin/bash
# ============================================================
#  Blind Assist Hat — Raspberry Pi Setup Script
#  Run once after cloning the repo:
#      chmod +x install.sh && ./install.sh
# ============================================================
set -e

echo "================================================"
echo "  Blind Assist Hat — Dependency Installer"
echo "================================================"

# ── System packages ──────────────────────────────────────────
echo "[1/4] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    espeak \
    alsa-utils \
    mpg123 \
    fswebcam \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    ffmpeg \
    libcamera-apps

# ── Python virtual environment ────────────────────────────────
echo "[2/4] Creating Python virtual environment..."
# --system-site-packages lets us use the system picamera2
python3 -m venv --system-site-packages venv

# ── Python packages ────────────────────────────────────────────
echo "[3/4] Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

# ── .env check ────────────────────────────────────────────────
echo "[4/4] Checking .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ⚠  Created .env from .env.example — please add your OPENAI_API_KEY."
else
    echo "  ✓ .env found."
fi

echo ""
echo "================================================"
echo "  Setup complete!"
echo "  1. Edit .env and add your OPENAI_API_KEY"
echo "  2. Run:  bash start.sh"
echo "================================================"
