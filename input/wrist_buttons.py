import time
import sys

# Keep global references to Button objects so they aren't garbage collected!
_buttons = []

def setup_buttons(callback_fn):
    """
    Sets up the GPIO pins for the 4 wrist buttons using gpiozero.
    callback_fn should accept an integer representing the PIN pressed.
    """
    try:
        from gpiozero import Button
    except ImportError:
        print("DEBUG: gpiozero not installed. Physical buttons will not work.")
        return

    from config.gpio_map import BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT
    pins = [BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT]
    
    for pin in pins:
        try:
            # Internal pull-up is True by default for Button, bounce_time handles debouncing
            btn = Button(pin, bounce_time=0.2)
            
            # gpiozero passes the button object to the callback if it takes an argument,
            # but we need to pass the PIN NUMBER explicitly to match the existing callback_fn interface.
            # We use a default argument in the lambda to capture the current iteration's button object!
            btn.when_pressed = lambda b=btn: callback_fn(b.pin.number)
            
            _buttons.append(btn)
        except Exception as e:
            print(f"DEBUG: Failed to initialize gpiozero Button on pin {pin}: {e}")

