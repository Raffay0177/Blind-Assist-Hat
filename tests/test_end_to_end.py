import sys
import os
import time
from unittest.mock import MagicMock

# 1. Mock hardware dependencies globally so Windows doesn't crash on import
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()
sys.modules['pyaudio'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()

# 2. Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dispatcher import handle_button_press
from config.gpio_map import BTN_1_SCENE, BTN_2_TEXT, BTN_3_NAV, BTN_4_REPEAT
from core.state import state

def test_flow():
    print("--- Starting End-to-End Mock Test ---\n")
    
    # Test 1. Describe Scene
    handle_button_press(BTN_1_SCENE)
    assert "Mocked vision analysis response" in state.last_output, "State did not cache scene description"
    print("-> Scene describe logic passed.\n")
    time.sleep(1)

    # Test 2. Read Text
    handle_button_press(BTN_2_TEXT)
    assert "Mocked vision analysis response" in state.last_output, "State did not cache text read"
    print("-> Text reading logic passed.\n")
    time.sleep(1)

    # Test 3. Navigation Toggle
    assert state.nav_mode_active == False, "Nav mode should default to False"
    handle_button_press(BTN_3_NAV)
    assert state.nav_mode_active == True, "Nav mode did not activate"
    print("-> Navigation toggle logic passed.\n")
    time.sleep(1)

    # Test 4. Repeat Last
    handle_button_press(BTN_4_REPEAT)
    print("-> Repeat last logic passed.\n")
    
    print("--- All tests completed successfully! ---")

if __name__ == "__main__":
    test_flow()
