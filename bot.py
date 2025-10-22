import os
import json
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
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
    return "✅ Василий работает и слушает Telegram!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print("📩 Получен апдейт от Telegram:")
        print(json.dumps(data, ensure_ascii=False, indent=2))

        update = Update.de_json(data, bot)

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Добавляем задачу в текущий event loop
        loop.create_task(application.process_update(update))

    except Exception as e:
        import traceback
        print("❌ Ошибка при обработке апдейта:", e)
        print(traceback.format_exc())  # выведет полный стек ошибки
        return "error", 500

    return "ok", 200

# === Telegram логика ===
async def start(update, context):
    await update.message.reply_text("Здравствуйте! Я Василий 🤖. Что хотите найти?")

async def handle_message(update, context):
    text = update.message.text.strip()
    if any(w in text.lower() for w in ["найди", "ищи", "поставщик", "где купить", "производитель"]):
        await update.message.reply_text("🔍 Думаю над ответом...")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты — помощник по поиску поставщиков в России."},
                    {"role": "user", "content": text}
                ]
            )
            reply = response["choices"][0]["message"]["content"].strip()
            await update.message.reply_text(reply)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к OpenAI: {e}")
    else:
        await update.message.reply_text("Напишите, что искать, например: 'поставщик бетона в Москве'.")


# === Telegram приложение ===
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# === Асинхронная инициализация и запуск ===
async def main():
    print("🌀 Инициализация Telegram-приложения...")
    await application.initialize()

    print("🔧 Удаление старого вебхука...")
    await bot.delete_webhook()

    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    print(f"🌐 Установка нового вебхука: {webhook_url}")
    await bot.set_webhook(url=webhook_url)

    print("✅ Telegram-приложение инициализировано и вебхук установлен.")
    print("🚀 Запуск Flask-сервера...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


if __name__ == "__main__":
    asyncio.run(main())
