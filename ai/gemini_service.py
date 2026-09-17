import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()


# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured in .env"
    )


# Create Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Gemini model
MODEL_NAME = "gemini-3.6-flash"


def generate_response(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the response.
    """

    if not prompt.strip():
        return "Please provide a prompt."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response.text:
            return "Gemini returned an empty response."

        return response.text.strip()

    except Exception as exc:
        print("Gemini API error:", exc)

        return (
            "Sorry, I could not connect to Gemini."
        )