import os
import requests
import feedparser
from datetime import datetime
import random

# --- CONFIG ---
CHAT_ID = os.environ.get("CHAT_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Feeds reales
FEEDS = [
    "https://www.investing.com/rss/crypto-news.xml",       # BTC y crypto
    "https://www.investing.com/rss/commodities-news.xml",  # oro, petróleo, commodities
    "https://www.investing.com/rss/market-news.xml",       # mercado general
]

# Palabras clave para filtrar noticias importantes
KEYWORDS = ["Bitcoin", "BTC", "Oro", "Trump", "Inflación", "PIB", "EEUU", "Europa"]

# Noticias simuladas para pruebas
SIMULATED_NEWS = [
    "🔥 Mister Strategy compra 1000 BTC como loco",
    "💹 Oro alcanza máximo histórico hoy",
    "📈 Nasdaq sube 3% tras anuncios de política económica",
    "💰 BTC rompe los 60k dólares, traders sorprendidos",
    "🌍 Europa publica datos macroeconómicos sorprendentes"
]

# --- FUNCIONES ---
def get_latest_news():
    news_list = []
    # Leer feeds reales
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
                })
    # Agregar noticias simuladas para pruebas
    for sim in SIMULATED_NEWS:
        news_list.append({
            "title": sim,
            "link": "https://t.me",
            "published": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        })
    # Mezclar las noticias para que parezcan más aleatorias
    random.shuffle(news_list)
    return news_list

def send_to_telegram(news_list, bot_token, chat_id):
    for news in news_list:
        text = f"📰 {news['title']}\n📅 {news['published']}\n🔗 {news['link']}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        try:
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                print(f"Error al enviar noticia: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

# --- MAIN ---
if __name__ == "__main__":
    news = get_latest_news()
    if news:
        send_to_telegram(news, BOT_TOKEN, CHAT_ID)
    else:
        print("No hay noticias nuevas para enviar.")
