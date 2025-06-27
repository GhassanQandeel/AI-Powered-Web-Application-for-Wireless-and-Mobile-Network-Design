import os
import requests

# ✅ Use Gemini 2.5 Flash with v1beta
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

def ask_gemini(prompt: str) -> str:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        return "Gemini API key is missing"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload
    )

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return f"Gemini Error: {response.status_code} - {response.text}"
