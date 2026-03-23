from config.gpio_map import BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT
from core.state import state
from ai.vision import describe_scene, read_text
from ai.tts import speak

def handle_button_press(channel):
    """ Routes the button press to the corresponding module """
    if channel == BTN_1_SCENE:
        print("\n[Button 1] Describe Scene triggered.")
        text = describe_scene()
        state.set_last_output(text)
        speak(text)
        
    elif channel == BTN_2_TEXT:
        print("\n[Button 2] Read Text triggered.")
        text = read_text()
        state.set_last_output(text)
        speak(text)
        
    elif channel == BTN_3_NAV:
        print("\n[Button 3] Navigation Mode toggled.")
        is_active = state.toggle_nav_mode()
        msg = "Navigation mode activated." if is_active else "Navigation mode deactivated."
        print(msg)
        speak(msg)
        
    elif channel == BTN_4_REPEAT:
        print("\n[Button 4] Repeat Last Output triggered.")
        if state.last_output:
            speak(state.last_output)
        else:
            speak("Nothing to repeat.")
