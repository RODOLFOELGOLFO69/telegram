import os
import requests
from datetime import datetime, timedelta
import feedparser
from openai import OpenAI

# ---------------- CONFIG ----------------

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------ HELPERS ----------------

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def get_news(query, max_articles=5):
    url = (
        f"https://newsapi.org/v2/everything?q={query}&language=en"
        f"&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    )
    r = requests.get(url)
    data = r.json()
    if "articles" not in data:
        return []
    return [f"• {a['title']}" for a in data["articles"][:max_articles]]

def get_macro_news():
    topics = ["inflation", "interest rates", "Federal Reserve", "ECB", "BoJ", "IMF", "GDP"]
    news = []
    for t in topics:
        news.extend(get_news(t))
    return news

def get_geopolitics_news():
    topics = ["war", "Russia Ukraine", "China Taiwan", "Middle East", "NATO"]
    news = []
    for t in topics:
        news.extend(get_news(t))
    return news

def get_trump_news():
    topics = ["Donald Trump", "US Election", "Republicans", "White House"]
    news = []
    for t in topics:
        news.extend(get_news(t))
    return news

def get_crypto_news():
    return get_news("Bitcoin BTC crypto") + get_news("Ethereum ETH crypto")

# ------------------ BTC FUNCTIONS ----------------

def get_btc_price():
    r = requests.get("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
    return float(r.json()["bpi"]["USD"]["rate_float"])

def btc_alert(last_price_file="btc_last_price.txt"):
    price = get_btc_price()
    last_price = None
    if os.path.exists(last_price_file):
        with open(last_price_file) as f:
            last_price = float(f.read())
    if last_price:
        change = ((price - last_price) / last_price) * 100
        if abs(change) >= 2:
            arrow = "📈" if change > 0 else "📉"
            send_telegram(f"{arrow} *ALERTA BTC*\nCambio: {change:.2f}%\nPrecio: {price}$")
    with open(last_price_file, "w") as f:
        f.write(str(price))

def daily_btc_analysis():
    price = get_btc_price()
    prompt = f"""
Eres un analista profesional de criptomonedas.
Genera un análisis diario completo de Bitcoin:
- Precio actual: {price} USD
- Tendencia general
- Soportes y resistencias
- Volatilidad y riesgos
- Predicción próxima hora y día
Formato claro, profesional y humano.
"""
    r = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    analysis = r.choices[0].message.content
    send_telegram(f"📊 *ANÁLISIS DIARIO BTC*\n\n{analysis}")

# ------------------ MARKET OPENINGS ----------------

def market_openings():
    now = datetime.utcnow().strftime("%H:%M")
    openings = {
        "00:00": "🟢 *Apertura Mercado Tokio* 🇯🇵",
        "07:00": "🟢 *Apertura Mercado Europa* 🇪🇺",
        "14:30": "🟢 *Apertura Mercado USA* 🇺🇸"
    }
    if now in openings:
        send_telegram(openings[now])

# ------------------ STOCKS + FOREX ----------------

def get_stock_price(symbol):
    try:
        url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={NEWS_API_KEY}"
        r = requests.get(url).json()
        return r[0]["price"]
    except:
        return None

def stock_alerts():
    symbols = ["^GSPC", "^DJI", "^IXIC", "^GDAXI", "^N225"]
    msg = "📈 *Índices principales*\n"
    for s in symbols:
        price = get_stock_price(s)
        if price:
            msg += f"{s}: {price}$\n"
    send_telegram(msg)

def forex_alerts():
    symbols = ["EURUSD", "DXY"]
    msg = "💱 *Forex*\n"
    for s in symbols:
        price = get_stock_price(s)
        if price:
            msg += f"{s}: {price}\n"
    send_telegram(msg)

# ------------------ MAIN ----------------

def run_all():
    send_telegram("🤖 *Macro IA Bot ejecutando...*")
    btc_alert()
    market_openings()
    now_utc = datetime.utcnow().strftime("%H:%M")
    if now_utc == "14:00":
        daily_btc_analysis()
    news_list = []
    news_list.extend(get_macro_news())
    news_list.extend(get_geopolitics_news())
    news_list.extend(get_trump_news())
    news_list.extend(get_crypto_news())
    if news_list:
        text = "📰 *NOTICIAS MACRO + CRYPTO + GEOPOLÍTICA + TRUMP*\n\n"
        text += "\n".join(news_list)
        send_telegram(text)
    stock_alerts()
    forex_alerts()
    send_telegram("✅ *Macro IA Bot finalizado.*")

if __name__ == "__main__":
    run_all()
