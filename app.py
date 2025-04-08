from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 🔄 .env laden
load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY fehlt. Bitte in Render als Umgebungsvariable setzen.")

# 🔧 Gemini konfigurieren (REST)
genai.configure(api_key=GEMINI_API_KEY, transport="rest")

# 📤 Nachricht an Telegram senden
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print("📬 Telegram-Antwort:", response.status_code, response.text)
    except Exception as e:
        print(f"❗ Telegram-Fehler: {e}")

# 🤖 Antwort von Gemini holen (bei freien Eingaben)
def get_gemini_reply(user_msg):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-001")
        response = model.generate_content(
            user_msg,
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 512
            }
        )
        return response.text
    except Exception as e:
        print(f"❗ Gemini-Fehler: {e}")
        return "⚠️ Fehler beim Antworten mit Gemini."

# 🏠 Startseite
@app.route('/')
def home():
    return "✅ NemisUz Gemini-Bot ist online!"

# 🔄 Telegram Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"].get("text", "")

        print("📥 Eingehende Nachricht:", user_msg)

        # 🔁 Eingabe analysieren
        if user_msg == "/start":
            reply = (
                "👋 Salom! Ich bin *NemisUz*, dein zweisprachiger Deutsch-Coach 🇩🇪🇺🇿\n\n"
                "Verfügbare Befehle:\n"
                "• /lernen – Tagestraining\n"
                "• /prüfung – Prüfungsvorbereitung\n"
                "• /sprechtraining – Ausspracheübung\n\n"
                "Du kannst mir auch einfach eine Frage auf Deutsch oder Usbekisch stellen!"
            )
        elif user_msg == "/lernen":
            reply = (
                "📘 Heute üben wir:\n"
                "🔹 *Wort des Tages:* _die Wohnung_ – uy\n"
                "🔹 *Grammatik:* Artikel im Dativ – *Ich wohne in der Wohnung.*\n\n"
                "👉 Schreib jetzt deinen Beispielsatz mit *der Wohnung*!"
            )
        elif user_msg == "/prüfung":
            reply = (
                "📝 Welche Prüfung willst du üben?\n"
                "• telc B1\n• Goethe B2\n• TestDaF\n• ÖSD C1\n\n"
                "Schreib z. B. *telc B1 starten*"
            )
        elif user_msg == "/sprechtraining":
            reply = (
                "🎙️ Wiederhole diesen Satz laut:\n"
                "*Ich habe eine Wohnung in Berlin.*\n\n"
                "Schick mir eine Sprachnachricht – ich gebe dir Feedback (bald verfügbar)."
            )
        else:
            # Freitext an Gemini weitergeben
            reply = get_gemini_reply(user_msg)

        send_telegram_message(chat_id, reply)

    return "ok", 200

# 🟢 Lokaler Start (optional)
if __name__ == '__main__':
    app.run(debug=True)
