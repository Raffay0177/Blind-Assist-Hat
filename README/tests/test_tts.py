"""
test_tts.py
Tests Text-to-Speech on Windows using pyttsx3 (no API key needed).
Run:  python test_tts.py
"""

try:
    import pyttsx3
except ImportError:
    print("[ERROR] pyttsx3 not installed. Run: pip install pyttsx3")
    exit(1)

engine = pyttsx3.init()

# Optional: adjust speed and volume
engine.setProperty('rate', 150)    # words per minute (default ~200)
engine.setProperty('volume', 1.0)  # 0.0 to 1.0

print("[..] Speaking: 'Hello World'")
engine.say("Hello World")
engine.runAndWait()
print("[OK] Done!")
