import os
import requests
import openai

# --- CONFIG ---
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Inicializar cliente OpenAI (API >=1.0)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ---------- FUNCIONES ----------

def send_message(text):
    """Envía mensaje a Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print(f"Error Telegram: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

def generate_btc_report():
    """Genera boletín diario de BTC profesional usando OpenAI"""
    system_prompt = (
        "Eres un analista financiero experto en Bitcoin. "
        "Genera un boletín diario de BTC en formato Telegram, claro y profesional, "
        "con precio actual, sentimiento de mercado, volatilidad, niveles técnicos "
        "(soporte, resistencia, pivote diario), resumen del día, eventos y estrategia. "
        "Usa emojis donde sea apropiado."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Genera el boletín diario de BTC para hoy con datos recientes y reales."}
            ],
            max_tokens=600,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generando boletín BTC: {e}"

def send_btc_report():
    """Genera y envía el boletín a Telegram"""
    report = generate_btc_report()
    send_message(f"📊 Boletín diario BTC\n\n{report}")

# ---------- MAIN ----------

if __name__ == "__main__":
    # Ejecutar siempre que se llame (para probar manualmente)
    send_btc_report()
