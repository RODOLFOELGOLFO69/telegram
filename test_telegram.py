import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🔧 Test directo desde GitHub Actions.\nSi ves esto, el bot funciona."
}

r = requests.post(url, data=payload)
print("STATUS:", r.status_code)
print("RESPONSE:", r.text)

