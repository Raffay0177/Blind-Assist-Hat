import os
import subprocess
from openai import OpenAI
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def speak(text):
    """
    Text-to-Speech (TTS) function using OpenAI's highly realistic TTS.
    Falls back to espeak if OpenAI key is missing or the internet fails.
    """
    print(f"🔊 [TTS]: {text}")
    
    if not client:
        _fallback_espeak(text)
        return
        
    audio_file = "/tmp/speech_output.wav"
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # Highly realistic, neutral AI voice
            input=text,
            response_format="wav" # WAV allows us to play directly with 'aplay' without extra dependencies
        )
        response.write_to_file(audio_file)
        
        # 'aplay' is built securely into all Raspberry Pi/Linux distributions
        subprocess.run(["aplay", "-q", audio_file], check=False)
        
    except Exception as e:
        print(f"DEBUG: OpenAI TTS Failed ({e}), falling back to espeak...")
        _fallback_espeak(text)

def _fallback_espeak(text):
    text = text.replace(" ", "_")  # Replace spaces with underscores to prevent parsing issues
    try:
        subprocess.run((
            "espeak \"" + text + "\" 2>/dev/null"
        ).split(" "), check=False)
    except FileNotFoundError:
        pass # Ignore if espeak is not installed (e.g. testing on Windows)


