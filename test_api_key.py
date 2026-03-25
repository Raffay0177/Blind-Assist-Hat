"""
test_api_key.py
Run this to verify your OpenAI API key works before deploying to the Pi.
Usage:  python test_api_key.py
"""

import os
import sys

# ── Load .env ──────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] .env file loaded")
except ImportError:
    print("[WARN] python-dotenv not installed – reading env vars directly")

# ── Check key is present ───────────────────────────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "your_openai_key_here":
    print("[ERROR] OPENAI_API_KEY is not set or still has the placeholder value.")
    print("        Edit your .env file and add your real key.")
    sys.exit(1)

print(f"[OK] Key found: {api_key[:8]}{'*' * (len(api_key) - 8)}")

# ── Test with a real API call ──────────────────────────────────────────────
try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] openai package not installed. Run: pip install openai")
    sys.exit(1)

print("[..] Sending a test request to OpenAI...")

try:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",          # cheap model – just for testing
        messages=[{"role": "user", "content": "Say 'API key works!' and nothing else."}],
        max_tokens=20,
    )
    reply = response.choices[0].message.content.strip()
    print(f"[OK] API responded: {reply}")
    print("\n✅ Your API key is valid and working!")

except Exception as e:
    print(f"\n[ERROR] API call failed: {e}")
    print("\n❌ Key is set but the request was rejected.")
    print("   Common causes:")
    print("   • Invalid / expired key")
    print("   • No billing set up on your OpenAI account")
    print("   • Rate limit hit")
    sys.exit(1)
