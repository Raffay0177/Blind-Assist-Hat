import time
import os

try:
    from picamera2 import Picamera2  # type: ignore
    hardware_available = True
except ImportError:
    hardware_available = False

def capture_image(filename="capture.jpg"):
    """ Captures an image using PiCamera2 and returns the filepath """
    if not hardware_available:
        print("📸 [MOCK CAMERA] Click! Captured simulated image.")
        return "mocked_capture.jpg"
        
    try:
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"size": (1280, 720)}))
        picam2.start()
        time.sleep(1) # Let sensor adjust to lighting
        
        filepath = os.path.join(os.path.dirname(__file__), "..", filename)
        picam2.capture_file(filepath)
        picam2.stop()
        return filepath
    except Exception as e:
        print(f"Camera error: {e}")
        return None
