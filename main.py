import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from openai import OpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

SYSTEM_PROMPT = "Sei un assistente utile, chiaro e diretto."

@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text or ""

    # Nuova API (openai>=1.x)
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )

    reply = resp.output_text
    await message.answer(reply)

@app.post("/webhook")
async def telegram_webhook(req: Request):
    update = Update.model_validate(await req.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.get("/")
def health():
    return {"status": "alive"}
