#!/bin/bash
# Navigate to the specific directory on the Raspberry Pi
cd ~/Desktop/BOH/Blind-Assist-Hat

# Activate the virtual environment
source venv/bin/activate

# Run the main program
echo "Starting Blind Assist Hat..."
python -m core.main
