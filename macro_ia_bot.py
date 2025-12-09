import os
import requests
import feedparser
from datetime import datetime
import openai

# --- CONFIG ---
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

# Feeds macroeconómicos
FEEDS = [
    "https://www.investing.com/rss/economic-calendar.xml",
    "https://www.investing.com/rss/market-news.xml"
]

KEYWORDS = ["PIB", "Inflación", "Tipos de interés", "EEUU", "Europa", "Mercados", "Recesión"]

# --- FUNCIONES ---
def get_latest_news():
    news_list = []
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if any(keyword.lower() in entry.title.lower() for keyword in KEYWORDS):
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
                })
    return news_list

def analyze_news_with_gpt(news_item):
    prompt = f"""
Analiza esta noticia macroeconómica y responde en formato:
1. Resumen breve de la noticia.
2. Relevancia: Alta, Media o Baja.
3. Breve previsión económica (1-2 frases).

Noticia: {news_item['title']}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Error al enviar noticia: {response.text}")

# --- MAIN ---
if __name__ == "__main__":
    news_list = get_latest_news()
    if not news_list:
        print("No hay noticias relevantes para enviar.")
    for news in news_list:
        analysis = analyze_news_with_gpt(news)
        text = f"📰 {news['title']}\n📅 {news['published']}\n🔗 {news['link']}\n\n{analysis}"
        send_to_telegram(text)
