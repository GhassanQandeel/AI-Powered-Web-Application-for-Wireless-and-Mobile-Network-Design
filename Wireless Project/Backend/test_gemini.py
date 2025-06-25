import requests

API_KEY = "AIzaSyAIQotwSfy9WhhpG1NX3lvnABjVCSTucmU"  # ← paste your key here
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

headers = {
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Explain OFDM in simple terms"}
            ]
        }
    ]
}

response = requests.post(f"{GEMINI_URL}?key={API_KEY}", headers=headers, json=payload)

try:
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    print("✅ Gemini response:")
    print(text)
except Exception:
    print("❌ Failed:", response.status_code)
    print(response.text)
