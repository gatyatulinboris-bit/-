import os
from flask import Flask, request
from telegram import Bot, Update, ParseMode
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# --- Конфиг ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8396494240:AAG3rJjtm6CXCqfrq8XgOGSncI_bYNe0Cwc")
ALLOWED_USERS = {7299174753}  # Допуск по ID

# --- Flask + Telegram ---
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
# Dispatcher из PTB v13 — синхронный, без asyncio, идеально для Render Free
dispatcher = Dispatcher(bot, update_queue=None, workers=0, use_context=True)


# --- Хелперы доступа ---
def is_allowed(update: Update) -> bool:
    try:
        uid = update.effective_user.id
        return uid in ALLOWED_USERS
    except Exception:
        return False


# --- Хендлеры ---
def start(update, context):
    if not is_allowed(update):
        update.message.reply_text("🚫 Доступ ограничен. Обратитесь к администратору.")
        return
    update.message.reply_text(
        "Здравствуйте! Я Василий — помощник по поиску поставщиков в строительстве (Россия). "
        "Напишите, что именно нужно найти."
    )


def handle_text(update, context):
    if not is_allowed(update):
        update.message.reply_text("🚫 Доступ ограничен. Обратитесь к администратору.")
        return

    text = update.message.text.strip()

    # Пока MVP: короткий «заглушка»-ответ по строительным поставщикам.
    # (Позже подключим поиск и базу)
    reply = (
        "Понял запрос: *{}*\n"
        "Я ищу строительных поставщиков по России. На старте выдам 2-3 варианта и уточню детали.\n"
        "_Скоро добавим обновляемую базу и умный поиск._"
    ).format(text)

    update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


# --- Регистрация хендлеров ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))


# --- Webhook endpoints ---
@app.route("/", methods=["GET"])
def index():
    return "Vasiliy-bot is alive", 200


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
    except Exception as e:
        print("Webhook error:", e)
    return "OK", 200


if __name__ == "__main__":
    # Локальный запуск (на Render не используется, запускается startCommand)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
