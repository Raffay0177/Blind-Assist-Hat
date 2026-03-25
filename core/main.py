import time
import threading
import sys

# Attempt GPIO import. If failing, mock it globally so other modules don't crash.
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

from config.gpio_map import BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT
from input.wrist_buttons import setup_buttons
from core.dispatcher import handle_button_press
from ai.navigation import setup as nav_setup, loop as nav_loop, destroy as nav_destroy

def main():
    print("Initializing Blind Assist Hat core system...")
    
    if hardware_available:
        GPIO.setwarnings(False)
        GPIO.cleanup() # Reset any pins leftover from an old crash
        GPIO.setmode(GPIO.BCM)
    else:
        print("Running in MOCK mode.")
    
    # 1. Setup Ultrasonics
    nav_setup()
    
    # 2. Setup Buttons
    try:
        setup_buttons(handle_button_press)
    except Exception as e:
        print(f"WARN: Could not setup buttons: {e}")
    
    # 3. Start Navigation Thread
    # The navigation loop runs infinitely, but inside it respects state.nav_mode_active
    nav_thread = threading.Thread(target=nav_loop, daemon=True)
    nav_thread.start()
    
    print("\n--- System Ready ---")
    print("Waiting for input. Press Ctrl+C to exit.")
    if not hardware_available:
        print("HINT: You can inject mocked hardware traces via unit tests to test functionality end-to-end.")
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down system...")
        nav_destroy()
        if hardware_available:
            GPIO.cleanup()

if __name__ == "__main__":
    main()
