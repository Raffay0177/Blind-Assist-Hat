"""
test_buttons.py
A simple script to test if the physical buttons are communicating with the Raspberry Pi.
Run: python3 test_buttons.py
"""

import time
import sys

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("[ERROR] RPi.GPIO not installed. This script must be run on a Raspberry Pi.")
    sys.exit(1)

# Hardcoded pin mappings for easy testing and modification
BTN_1_SCENE = 16
BTN_2_TEXT = 20
BTN_3_NAV = 21
BTN_4_REPEAT = 12

def button_callback(channel):
    """Callback function triggered on button press."""
    button_name = "Unknown"
    if channel == BTN_1_SCENE:
        button_name = "Button 1 (Describe Scene)"
    elif channel == BTN_2_TEXT:
        button_name = "Button 2 (Read Text)"
    elif channel == BTN_3_NAV:
        button_name = "Button 3 (Toggle Nav Mode)"
    elif channel == BTN_4_REPEAT:
        button_name = "Button 4 (Repeat Last)"
    
    print(f"\n[OK] Detected Press on {button_name} (GPIO {channel})")

def main():
    print("=" * 50)
    print("  Blind Assist Hat – Button Communication Test")
    print("=" * 50)
    print("This script will help you verify if your buttons are wired correctly.")
    print("Press Ctrl+C to exit.\n")

    # Set up GPIO mode
    GPIO.setmode(GPIO.BCM)
    
    buttons = [BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT]
    
    polling_mode = False
    for btn in buttons:
        print(f"Initializing GPIO {btn}...")
        GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        try:
            GPIO.add_event_detect(btn, GPIO.FALLING, callback=button_callback, bouncetime=300)
        except RuntimeError as e:
            print(f"  [WARN] Edge detection failed for GPIO {btn}: {e}")
            polling_mode = True
            
    if polling_mode:
        print("\n[INFO] Edge detection failed (likely running on Bookworm). Falling back to basic polling mode.")
        print("Ready! Press any button on the wrist pad now...")
        
        last_state = {btn: GPIO.HIGH for btn in buttons}
        try:
            while True:
                for btn in buttons:
                    current_state = GPIO.input(btn)
                    if current_state == GPIO.LOW and last_state[btn] == GPIO.HIGH: # Falling edge
                        button_callback(btn)
                    last_state[btn] = current_state
                time.sleep(0.05) # Prevent 100% CPU usage
        except KeyboardInterrupt:
            print("\nExiting test...")
        finally:
            GPIO.cleanup()
            print("GPIO cleaned up. Goodbye!")
    else:
        print("\nReady! Press any button on the wrist pad now...")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting test...")
        finally:
            GPIO.cleanup()
            print("GPIO cleaned up. Goodbye!")


if __name__ == "__main__":
    main()
