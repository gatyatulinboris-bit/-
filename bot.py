import os
import json
from datetime import datetime
from flask import Flask, request
import openai
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")  # https://vasiliy-bot.onrender.com

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)

# === Flask сервер ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Василий работает!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return 'ok'


# === Основная логика ===
async def start(update, context):
    await update.message.reply_text(
        "Здравствуйте! Я Василий 🤖.\n"
        "Помогаю искать поставщиков и производителей в России.\n"
        "Что нужно найти?"
    )

async def handle_message(update, context):
    text = update.message.text

    if any(w in text.lower() for w in ["найди", "ищи", "поставщик", "где купить", "производитель"]):
        await update.message.reply_text("🔍 Ищу варианты, секундочку...")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты — помощник по поиску поставщиков и производителей в России."},
                    {"role": "user", "content": text}
                ]
            )
            reply = response["choices"][0]["message"]["content"].strip()
            await update.message.reply_text(reply)

        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к ИИ: {e}")
    else:
        await update.message.reply_text("Уточните, что нужно найти, например: 'поставщик бетона в Москве'.")


# === Настройка Telegram-приложения ===
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === Запуск на Render ===
if __name__ == "__main__":
    import asyncio

    async def set_webhook():
        await bot.delete_webhook()
        await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
        print(f"✅ Вебхук установлен: {WEBHOOK_URL}/{BOT_TOKEN}")

    asyncio.run(set_webhook())

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
