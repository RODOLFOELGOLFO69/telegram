import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
import openai

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

# Feeds de noticias
FEEDS = [
    "https://www.investing.com/rss/crypto-news.xml",
    "https://www.investing.com/rss/commodities-news.xml",
    "https://www.investing.com/rss/market-news.xml",
]

# Palabras clave importantes
KEYWORDS = ["bitcoin", "btc", "oro", "trump", "inflación", "pib", "eeuu", "europa"]

# ---------- FUNCIONES ----------

def get_latest_news():
    news_list = []
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", "Sin fecha")
            })
    return news_list

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print(f"Error Telegram: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

def send_news():
    news = get_latest_news()
    if not news:
        send_message("⚠️ No se encontraron noticias nuevas.")
        return
    for n in news[:5]:  # solo los 5 primeros titulares
        text = f"📰 {n['title']}\n📅 {n['published']}\n🔗 {n['link']}"
        send_message(text)

def generate_btc_report():
    prompt = (
        "Haz un análisis diario de BTC en estilo profesional para traders: "
        "indica precio actual, tendencia, niveles importantes, y breve comentario sobre noticias relevantes."
    )
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=250
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error generando boletín BTC: {e}"

def send_btc_report():
    report = generate_btc_report()
    send_message(f"📊 Boletín diario BTC (20:45 España)\n\n{report}")

# ---------- MAIN ----------

if __name__ == "__main__":
    # Hora actual España (CET)
    now_utc = datetime.now(timezone.utc)
    now_cet = now_utc + timedelta(hours=1)

    # Enviar boletín BTC a las 20:45
    if now_cet.hour == 20 and now_cet.minute == 45:
        send_btc_report()
    else:
        send_news()
