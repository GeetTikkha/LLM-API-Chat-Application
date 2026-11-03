"""Basic configuration check; does not print or expose the API key."""
import os
from openai import OpenAI

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("Set OPENAI_API_KEY before running this script.")
client = OpenAI()
print("OpenAI client initialized. Configured model:", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
