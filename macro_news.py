import os
import requests
import feedparser
from datetime import datetime

# --- CONFIG ---
CHAT_ID = os.environ.get("CHAT_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Feeds RSS de noticias económicas y financieras (EEUU y Europa)
FEEDS = [
    "https://www.investing.com/rss/economic-calendar.xml",  # calendario económico
    "https://www.investing.com/rss/crypto-news.xml",       # noticias BTC/crypto
    "https://www.investing.com/rss/commodities-news.xml",  # oro, petróleo, commodities
    "https://www.investing.com/rss/market-news.xml"        # mercado general
]

# --- FUNCIONES ---
def get_latest_news():
    news_list = []
    now = datetime.utcnow()
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            # Opcional: filtrar solo noticias de hoy (UTC)
            # published_time = datetime(*entry.published_parsed[:6])
            # if published_time.date() != now.date():
            #     continue

            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", now.strftime("%Y-%m-%d %H:%M"))
            })
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
