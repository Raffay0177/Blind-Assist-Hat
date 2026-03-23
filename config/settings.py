import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TTS_VOICE = os.getenv("TTS_VOICE", "en-US")
OBSTACLE_WARN_DISTANCE_CM = int(os.getenv("OBSTACLE_WARN_DISTANCE_CM", "100"))
