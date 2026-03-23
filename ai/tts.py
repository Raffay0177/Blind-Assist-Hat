import subprocess

def speak(text):
    """
    Text-to-Speech (TTS) function.
    Uses espeak to speak the given text.
    """
    print(f"🔊 [TTS]: {text}")
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    try:
        subprocess.run((
            "espeak \"" + text + "\" 2>/dev/null"
        ).split(" "), check=False)  # Construct the command and split into tokens for subprocess.run
    except FileNotFoundError:
        pass # Ignore if espeak is not installed (e.g. testing on Windows)
