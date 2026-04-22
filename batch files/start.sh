#!/bin/bash
# ============================================================
#  Blind Assist Hat — Launch Script
#  Usage: bash start.sh
# ============================================================

# Navigate to script directory (works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "ERROR: venv not found. Run ./install.sh first."
    exit 1
fi
source venv/bin/activate

# Verify .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and fill in your API key."
    exit 1
fi

echo "Starting Blind Assist Hat..."
python blind_assist.py
