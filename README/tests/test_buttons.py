"""
test_buttons.py
A simple script to test if the physical buttons are communicating with the Raspberry Pi.
Uses gpiozero, which is the modern standard for Raspberry Pi hardware control.
Run: python3 test_buttons.py
"""

import sys

try:
    from gpiozero import Button
    from signal import pause
except ImportError:
    print("[ERROR] gpiozero not installed. This script must be run on a Raspberry Pi.")
    print("        You can install it with: sudo apt install python3-gpiozero")
    sys.exit(1)

# Hardcoded pin mappings for easy testing and modification
BTN_1_SCENE = 16
BTN_2_TEXT = 20
BTN_3_NAV = 21
BTN_4_REPEAT = 12

def on_button_1_pressed():
    print("\n[OK] Detected Press on Button 1 (Describe Scene) (GPIO 16)")

def on_button_2_pressed():
    print("\n[OK] Detected Press on Button 2 (Read Text) (GPIO 20)")

def on_button_3_pressed():
    print("\n[OK] Detected Press on Button 3 (Toggle Nav Mode) (GPIO 21)")

def on_button_4_pressed():
    print("\n[OK] Detected Press on Button 4 (Repeat Last) (GPIO 12)")

def main():
    print("=" * 50)
    print("  Blind Assist Hat – GPIOZero Button Test")
    print("=" * 50)
    print("This script uses 'gpiozero' to verify if your buttons are wired correctly.")
    print("Press Ctrl+C to exit.\n")

    # gpiozero automatically handles debouncing (bounce_time) and internal pull-ups!
    # By default, Button assumes the button connects to GND (pull_up=True).
    print("Initializing GPIO 16...")
    btn1 = Button(BTN_1_SCENE, bounce_time=0.1)
    btn1.when_pressed = on_button_1_pressed
    
    print("Initializing GPIO 20...")
    btn2 = Button(BTN_2_TEXT, bounce_time=0.1)
    btn2.when_pressed = on_button_2_pressed
    
    print("Initializing GPIO 21...")
    btn3 = Button(BTN_3_NAV, bounce_time=0.1)
    btn3.when_pressed = on_button_3_pressed
    
    print("Initializing GPIO 12...")
    btn4 = Button(BTN_4_REPEAT, bounce_time=0.1)
    btn4.when_pressed = on_button_4_pressed

    print("\nReady! Press any button on the wrist pad now...")
    
    try:
        pause()  # This keeps the script running silently while waiting for interrupts
    except KeyboardInterrupt:
        print("\nExiting test. GPIO cleaned up automatically. Goodbye!")

if __name__ == "__main__":
    main()
