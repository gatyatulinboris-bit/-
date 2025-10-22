import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")  # https://vasiliy-bot.onrender.com

# Flask приложение
app = Flask(__name__)

# Создаём Telegram-приложение
application = Application.builder().token(BOT_TOKEN).build()

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я жив 🟢")

# --- Обработка любых сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    print(f"📩 Получено сообщение от {user.first_name}: {text}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я жив 🟢")

# Добавляем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask route для вебхука ---
@app.route("/", methods=["GET"])
def index():
    return "Бот работает ✅", 200

@app.route("/", methods=["POST"])
def webhook():
    """Основной webhook endpoint"""
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        # Обрабатываем входящее обновление асинхронно
        application.create_task(application.process_update(update))
        return "ok", 200
    except Exception as e:
        print("Ошибка при обработке апдейта:", e)
        return "error", 500

# --- Запуск приложения ---
if __name__ == "__main__":
    import asyncio
    import telegram

    async def set_webhook():
        bot = telegram.Bot(BOT_TOKEN)
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(url=f"{WEBHOOK_URL}")
        print(f"✅ Вебхук установлен: {WEBHOOK_URL}")

    asyncio.run(set_webhook())

    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
