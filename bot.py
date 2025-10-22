import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === Переменные окружения ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Flask приложение ===
app = Flask(__name__)

# === Telegram приложение ===
application = Application.builder().token(BOT_TOKEN).build()

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! 👋 Я жив 🟢")

# === Ответ на любое сообщение ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    print(f"💬 Получено сообщение от {user.first_name}: {text}")
    await update.message.reply_text("Привет! Я жив 🟢")

# === Роут для Telegram вебхука ===
@app.route("/", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
    except Exception as e:
        print(f"Ошибка при обработке апдейта: {e}")
    return "ok", 200

# === Роут для проверки (GET-запрос) ===
@app.route("/", methods=["GET"])
def index():
    return "✅ VasiliyBot работает. Telegram Webhook активен!", 200

# === Добавляем обработчики ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Точка входа ===
if __name__ == "__main__":
    print("🚀 Запуск Flask сервера...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
