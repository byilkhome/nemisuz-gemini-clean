from flask import Flask, request
import requests
import os
import html
from dotenv import load_dotenv
import google.generativeai as genai

# 🔄 Umgebungsvariablen laden
load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY fehlt. Bitte in Render als Umgebungsvariable setzen.")

# 🔧 Gemini konfigurieren
genai.configure(api_key=GEMINI_API_KEY, transport="rest")

# 📤 Telegram Nachricht senden (HTML aktiviert)
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        print("📬 Telegram-Antwort:", response.status_code, response.text)
    except Exception as e:
        print(f"❗ Telegram-Fehler: {e}")

# 🧼 Benutzerinput & Gemini-Antwort HTML-sicher machen
def clean_user_input(text):
    return html.escape(text)

# 🤖 Gemini-Antwort holen
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
        return html.escape(response.text)
    except Exception as e:
        print(f"❗ Gemini-Fehler: {e}")
        return "⚠️ Fehler beim Antworten mit Gemini."

# 📋 Menütext
def get_main_menu():
    return (
        "📚 <b>Hauptmenü</b><br><br>"
        "📘 /lernen – Wortschatz & Grammatik<br>"
        "📝 /prüfung – Prüfungstraining (telc, Goethe, TestDaF)<br>"
        "🗣️ /sprechtraining – Aussprache üben<br><br>"
        "❓ Oder stelle mir deine Frage auf Deutsch oder Usbekisch!"
    )

@app.route('/')
def home():
    return "✅ NemisUz Gemini-Bot ist online!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_msg = data["message"].get("text", "").strip()

        print("📥 Eingehende Nachricht:", user_msg)

        # Eingabeverarbeitung
        if user_msg == "/start":
            reply = (
                "👋 <b>Salom!</b> Ich bin <b>NemisUz</b> – dein zweisprachiger Deutsch-Coach 🇩🇪🇺🇿<br><br>"
                + get_main_menu()
            )
        elif user_msg == "/lernen":
            reply = (
                "📘 <b>Heute üben wir:</b><br>"
                "🔹 <b>Wort des Tages:</b> <i>die Wohnung</i> – uy<br>"
                "🔹 <b>Grammatik:</b> Artikel im Dativ – <i>Ich wohne in der Wohnung.</i><br><br>"
                "👉 Schreib einen Beispielsatz mit <i>der Wohnung</i>!"
            )
        elif user_msg == "/prüfung":
            reply = (
                "📝 <b>Welche Prüfung möchtest du üben?</b><br>"
                "• telc B1<br>• Goethe B2<br>• TestDaF<br>• ÖSD C1<br><br>"
                "Schreib z. B. <i>telc B1 starten</i>"
            )
        elif user_msg == "/sprechtraining":
            reply = (
                "🎙️ <b>Wiederhole diesen Satz laut:</b><br>"
                "<i>Ich habe eine Wohnung in Berlin.</i><br><br>"
                "Schick mir eine Sprachnachricht – ich gebe dir Feedback (bald verfügbar)."
            )
        else:
            sanitized_input = clean_user_input(user_msg)
            reply = get_gemini_reply(sanitized_input)

        send_telegram_message(chat_id, reply)

    return "ok", 200

if __name__ == '__main__':
    app.run(debug=True)

