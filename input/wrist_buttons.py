import RPi.GPIO as GPIO  # type: ignore
from config.gpio_map import BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT

def setup_buttons(callback_fn):
    """
    Sets up the GPIO pins for the 4 wrist buttons and attaches interrupt handlers.
    callback_fn should accept an integer representing the PIN pressed.
    """
    buttons = [BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT]
    
    for btn in buttons:
        # Use internal pull-up resistors; buttons should connect pin to GND
        GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Bouncetime prevents double-triggers from noisy button contacts
        GPIO.add_event_detect(btn, GPIO.FALLING, 
                              callback=lambda channel, b=btn: callback_fn(b), 
                              bouncetime=300)
