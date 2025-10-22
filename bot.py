import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из переменных окружения
if not BOT_TOKEN:
    BOT_TOKEN = "8396494240:AAG3rJjtm6CXCqfrq8XgOGSncI_bYNe0Cwc"  # резерв, если не задано в Render

PORT = int(os.environ.get("PORT", 10000))

# === Flask-приложение ===
app = Flask(__name__)

# === Создание Telegram-приложения ===
application = Application.builder().token(BOT_TOKEN).build()

# === Обработчик команды /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я жив и готов работать!")

# === Обработчик любого текста ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    print(f"💬 Получено сообщение от {user.first_name}: {text}")
    await update.message.reply_text("Привет! Я жив 🟢")

# === Добавление хендлеров ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Обработка вебхука с любым путём (в том числе с токеном) ===
@app.route("/", methods=["POST"])
@app.route("/<path:path>", methods=["POST"])
def webhook(path=None):
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
        return "ok", 200
    except Exception as e:
        print(f"Ошибка при обработке апдейта: {e}")
        return "error", 500

# === Запуск Flask-сервера ===
if __name__ == "__main__":
    print("🚀 Запуск Flask сервера...")
    app.run(host="0.0.0.0", port=PORT)
