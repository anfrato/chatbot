import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.filters import CommandStart
from openai import OpenAI

# ======================
# ENV
# ======================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN env var")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY env var")

# OpenAI client (new SDK)
client = OpenAI(api_key=OPENAI_API_KEY)

# Telegram / FastAPI
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

SYSTEM_PROMPT = "Sei un assistente utile, chiaro e diretto."

# ======================
# HANDLERS
# ======================
@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "👋 Ciao! Sono *WarrenBot*.\n\n"
        "Scrivimi qualsiasi cosa e ti risponderò.\n\n"
        "✅ Bot online e pronto!",
        parse_mode="Markdown"
    )

@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text or ""
    user_text = user_text.strip()

    if not user_text:
        await message.answer("Mandami un testo 🙂")
        return

    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        )
        reply = resp.output_text or "Non ho una risposta pronta 😅"
        await message.answer(reply)
    except Exception:
        # Evita di leakare dettagli sensibili nei messaggi utente
        await message.answer("⚠️ Errore temporaneo. Riprova tra poco.")

# ======================
# WEBHOOK ENDPOINTS
# ======================
@app.post("/webhook")
async def telegram_webhook(req: Request):
    update = Update.model_validate(await req.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
def health():
    return {"status": "alive"}
