import time
import os
import subprocess
import shutil

try:
    from picamera2 import Picamera2  # type: ignore
    csi_available = True
except ImportError:
    csi_available = False

def capture_image(filename="capture.jpg"):
    """
    Captures an image using the available camera hardware.
    Prioritizes CSI Camera (Picamera2), falls back to USB Camera (fswebcam).
    """
    filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    
    # --- Try CSI Camera (Picamera2) ---
    if csi_available:
        try:
            picam2 = Picamera2()
            picam2.configure(picam2.create_preview_configuration(main={"size": (1280, 720)}))
            picam2.start()
            time.sleep(1) # Let sensor adjust to lighting
            picam2.capture_file(filepath)
            picam2.stop()
            return filepath
        except Exception as e:
            print(f"DEBUG: CSI Camera (Picamera2) failed: {e}")

    # --- Fallback: Try USB Camera (fswebcam) ---
    if shutil.which("fswebcam"):
        try:
            print("📸 [USB CAMERA] Using fswebcam to capture.")
            # -r 1280x720: resolution
            # -S 20: Skip 20 frames to let exposure settle (crucial for USB webcams)
            # --no-banner: hides timestamp banner
            subprocess.run(["fswebcam", "-r", "1280x720", "-S", "20", "--no-banner", filepath], check=True, capture_output=True)
            return filepath
        except Exception as e:
            print(f"DEBUG: USB Camera (fswebcam) failed: {e}")

    # --- MOCK fallback if no hardware is found ---
    print("📸 [MOCK CAMERA] Click! Captured simulated image.")
    return "mocked_capture.jpg"
