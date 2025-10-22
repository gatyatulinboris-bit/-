import os
import json
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import openai

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")  # https://vasiliy-bot.onrender.com

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)

# === Flask ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Василий работает!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    print("📩 Получен апдейт от Telegram:", json.dumps(data, ensure_ascii=False, indent=2))
    update = Update.de_json(data, bot)
    asyncio.run(application.process_update(update))
    return 'ok'


# === Telegram логика ===
async def start(update, context):
    await update.message.reply_text(
        "Здравствуйте! Я Василий 🤖.\n"
        "Помогаю искать поставщиков и производителей в России.\n"
        "Что нужно найти?"
    )

async def handle_message(update, context):
    text = update.message.text.strip()
    if any(w in text.lower() for w in ["найди", "ищи", "поставщик", "где купить", "производитель"]):
        await update.message.reply_text("🔍 Думаю над ответом, секундочку...")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        "Ты — Василий, помощник по поиску поставщиков и производителей в России. "
                        "Отвечай кратко, по делу, предлагай 2–3 направления поиска или конкретных поставщиков."
                    )},
                    {"role": "user", "content": text}
                ]
            )
            reply = response["choices"][0]["message"]["content"].strip()
            await update.message.reply_text(reply)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к OpenAI: {e}")
    else:
        await update.message.reply_text("Уточните, что нужно найти, например: 'поставщик бетона в Москве'.")


# === Настройка Telegram ===
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === Запуск вебхука ===
async def main():
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print(f"✅ Вебхук установлен: {WEBHOOK_URL}/{BOT_TOKEN}")
    print("🚀 Василий готов к работе!")

if __name__ == "__main__":
    asyncio.run(main())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
