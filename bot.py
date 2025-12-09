# bot.py
import os
import requests
import feedparser

# Leemos token y chat_id desde variables de entorno (más seguro)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ejemplo: @TuCanalPublico o -1001234567890 para privados

RSS_URL = "https://www.investing.com/rss/news_284.rss"  # fuente de noticias macro

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, data=data)
    # opcional: print(resp.status_code, resp.text)
    return resp

def generar_analisis_simple(titulo):
    """
    Generador simple (plantilla). Si transformers falla o para ahorrar tiempo,
    usamos esto: una frase corta basada en palabras clave.
    """
    t = titulo.lower()
    if "inflación" in t or "inflacion" in t:
        return "Posible presión alcista sobre precios; puede aumentar expectativas de subidas de tipos."
    if "bce" in t or "banco central europeo" in t or "fed" in t or "reserva federal" in t:
        return "Declaraciones de bancos centrales: potencial impacto en tipos y mercados."
    if "desempleo" in t or "paro" in t:
        return "Dato laboral importante: impacto en consumo y expectativas de política monetaria."
    if "pib" in t or "producto interior bruto" in t:
        return "Cambio en crecimiento económico: relevante para previsiones macro y mercados."
    if "inflation" in t or "employment" in t or "gdp" in t:
        return "Dato macro importante: puede mover expectativas de política monetaria."
    # fallback genérico
    return "Noticia macro con posible impacto sobre expectativas de política y mercados."

def main():
    # chequeo mínimo
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERROR: Pon TELEGRAM_TOKEN y CHAT_ID en las variables de entorno.")
        return

    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("No hay entradas en el RSS.")
        return

    noticia = feed.entries[0]
    titulo = noticia.title
    link = noticia.link

    # Generamos análisis simple (rápido y fiable)
    analisis = generar_analisis_simple(titulo)

    mensaje = (
        f"📰 *Noticia Macroeconómica*\n\n"
        f"*Titular:* {titulo}\n"
        f"🔗 {link}\n\n"
        f"📊 *Análisis automático:* {analisis}"
    )

    resp = send_msg(mensaje)
    print("Enviado, status:", resp.status_code)

if __name__ == "__main__":
    main()
