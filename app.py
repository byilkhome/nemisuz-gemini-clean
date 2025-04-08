from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env laden
load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY fehlt. Bitte in Render als Umgebungsvariable setzen.")

# Gemini konfigurieren (REST verwenden)
genai.configure(api_key=GEMINI_API_KEY, transport="rest")

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    # 🐞 Debug-Ausgaben:
    print("📨 Chat ID:", chat_id)
    print("📤 Gesendeter Text:", text)
    print("📦 API URL:", url)
    print("📦 Payload:", payload)

    try:
        response = requests.post(url, json=payload)
        print("📬 Telegram-Antwort:", response.status_code, response.text)
    except Exception as e:
        print(f"❗ Telegram-Fehler: {e}")

def get_gemini_reply(user_msg):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-001")
        response = model.generate_content(
            user_msg,
            generation_config={"temperature": 0.7, "top_p": 1, "top_k": 1, "max_output_tokens": 512}
        )
        return response.text
    except Exception as e:
        print(f"❗ Gemini-Fehler: {e}")
        return "⚠️ Antwortfehler bei Gemini."

@app.route('/')
def home():
    return "NemisUz Gemini-Bot ist online!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"].get("text", "")
        
        # Debug: Eingehende Nachricht
        print("📥 Eingehende Nachricht:", user_msg)

        if user_msg:
            reply = get_gemini_reply(user_msg)
            print("🤖 Antwort von Gemini:", reply)
            send_telegram_message(chat_id, reply)

    return "ok", 200

if __name__ == '__main__':
    app.run()
