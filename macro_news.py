import requests
import feedparser
from datetime import datetime, timedelta

# --- CONFIG ---
import os

CHAT_ID = os.environ.get("CHAT_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

FEEDS = [
    "https://www.investing.com/rss/economic-calendar.xml",  # ejemplo RSS
]

# --- FUNCIONES ---
def get_latest_news():
    news_list = []
    now = datetime.utcnow()
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            # Filtramos noticias del día
            published_time = datetime(*entry.published_parsed[:6])
            if published_time.date() == now.date():
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_time.strftime("%Y-%m-%d %H:%M")
                })
    return news_list

def send_to_telegram(news_list, bot_token, chat_id):
    for news in news_list:
        text = f"📰 {news['title']}\n📅 {news['published']}\n🔗 {news['link']}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, data=payload)

# --- MAIN ---
if __name__ == "__main__":
    news = get_latest_news()
    if news:
        send_to_telegram(news, BOT_TOKEN, CHAT_ID)
