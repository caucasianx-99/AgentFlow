
import os

from dotenv import load_dotenv
from google import genai


# Load the private API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in your .env file."
    )

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Send a simple test instruction
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=(
        "You are AgentFlow, an AI assistant. "
        "Introduce yourself in one short sentence."
    )
)

print("AgentFlow — Gemini Connection Test")
print("----------------------------------")
print(response.text)