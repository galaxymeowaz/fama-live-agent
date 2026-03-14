import os
from dotenv import load_dotenv
from google import genai

# FORCE override of cached system variables
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("FATAL ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

# DevSecOps Audit: Print only the last 4 chars to verify which key is loading
print(f"AUDIT: Using API Key ending in ...{api_key[-4:]}")

print("Initializing Gemini Client...")
client = genai.Client(api_key=api_key)

try:
    print("Pinging Google Servers...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Respond with exactly three words: Connection is live.'
    )
    print(f"AI RESPONSE: {response.text}")
except Exception as e:
    print(f"API FAILURE: {e}")