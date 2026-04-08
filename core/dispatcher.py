import threading
from config.gpio_map import BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT
from core.state import state
from ai.vision import describe_scene, read_text
from ai.tts import speak

def handle_button_press(channel):
    """ Routes the button press to the corresponding module """
    
    if state.is_processing:
        print("\n[BLOCKED] Command ignored, system is already processing a request.")
        return
        
    # Block all other features if Navigation Mode is active
    if state.nav_mode_active and channel != BTN_3_NAV:
        print("\n[BLOCKED] User attempted to use another feature while Nav Mode is active.")
        speak("Please exit navigation mode first.")
        return

    if channel == BTN_1_SCENE:
        state.is_processing = True
        print("\n[Button 1] Describe Scene triggered.")
        threading.Thread(target=speak, args=("Looking straight ahead...",), daemon=True).start()
        text = describe_scene()
        state.set_last_output(text)
        speak(text)
        state.is_processing = False
        
    elif channel == BTN_2_TEXT:
        state.is_processing = True
        print("\n[Button 2] Read Text triggered.")
        threading.Thread(target=speak, args=("Scanning for text...",), daemon=True).start()
        text = read_text()
        state.set_last_output(text)
        speak(text)
        state.is_processing = False
        
    elif channel == BTN_3_NAV:
        print("\n[Button 3] Navigation Mode toggled.")
        is_active = state.toggle_nav_mode()
        if is_active:
            msg = "Sonar navigation systems online. Obstacle detection engaged."
        else:
            msg = "Navigation mode offline. Returning to standby."
        print(msg)
        speak(msg)
        
    elif channel == BTN_4_REPEAT:
        print("\n[Button 4] Repeat Last Output triggered.")
        if state.last_output:
            speak(state.last_output)
        else:
            speak("Nothing to repeat.")
