import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
import openai

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Feeds de noticias macro y cripto
FEEDS = [
    "https://www.investing.com/rss/crypto-news.xml",
    "https://www.investing.com/rss/commodities-news.xml",
    "https://www.investing.com/rss/market-news.xml",
]

KEYWORDS = ["bitcoin", "btc", "oro", "trump", "inflación", "pib", "eeuu", "europa"]

# ---------- FUNCIONES ----------

def get_latest_news():
    news_list = []
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
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
    for n in news[:5]:
        text = f"📰 {n['title']}\n📅 {n['published']}\n🔗 {n['link']}"
        send_message(text)

def generate_btc_report():
    """
    Genera un boletín diario BTC estilo profesional con:
    - Precio actual
    - Sentimiento de mercado
    - Volatilidad
    - Niveles técnicos
    - Resumen del día
    """
    system_prompt = (
        "Eres un analista financiero profesional especializado en BTC y criptomonedas. "
        "Genera un boletín diario con formato de Telegram, estilo profesional y claro, "
        "incluyendo: precio actual, sentimiento de mercado, volatilidad, niveles técnicos "
        "(soporte, resistencia, pivotes), resumen del día, eventos importantes y estrategia."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Genera el boletín diario de BTC para hoy con datos recientes y reales."}
            ],
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generando boletín BTC: {e}"

def send_btc_report():
    report = generate_btc_report()
    send_message(f"📊 Boletín diario BTC (20:45 España)\n\n{report}")

# ---------- MAIN ----------

if __name__ == "__main__":
    # Hora España (CET)
    now_utc = datetime.now(timezone.utc)
    now_cet = now_utc + timedelta(hours=1)

    if now_cet.hour == 21 and now_cet.minute == 45:
        send_btc_report()
    else:
        send_news()

