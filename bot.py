import os
import json
import time
from datetime import datetime, timedelta
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from aiohttp import web

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
ALLOWED_USERS = {7299174753}  # ← твой Telegram ID
BOT_NAME = "василий"
LOG_FILE = "dialog_history.json"
DAYS_TO_KEEP = 30  # храним диалоги 30 дней

# === Проверка и создание файла истории ===
def ensure_log_file_exists():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print("[INFO] Файл истории диалогов создан (dialog_history.json)")
    else:
        print("[INFO] Файл истории найден ✅")

# === Сохранение истории ===
def save_dialog(user_id, message, reply):
    now = datetime.now()
    cutoff_date = now - timedelta(days=DAYS_TO_KEEP)
    data = []

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    # фильтруем старые записи
    data = [
        d for d in data
        if datetime.strptime(d.get("timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S") >= cutoff_date
    ]

    data.append({
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "message": message,
        "reply": reply
    })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === Приветствие ===
async def greet_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я Василий — помощник по поиску поставщиков и производителей в России 🇷🇺.\n"
        "Помогаю находить надёжных партнёров в строительстве, HVAC, автопроме, продуктах, одежде и других сферах.\n\n"
        "Что именно нужно найти?"
    )

# === Основная логика ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 У вас нет доступа к Василию.")
        return

    # приветствия
    if any(word in text.lower() for word in ["привет", "здравствуй", "добрый день", "хай"]):
        await update.message.reply_text("Здравствуйте 👋 Я Василий. Что нужно найти?")
        return

    # запрос на поиск
    if any(word in text.lower() for word in ["найди", "ищи", "поставщик", "производитель", "где купить", "закупка", "купить", "искать"]):
        await update.message.reply_text("🤖 Думаю над ответом, подбираю варианты...")

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "Ты — Василий, умный ассистент по закупкам в России. "
                        "Ты ищешь и предлагаешь 2–3 реальных варианта поставщиков или производителей по запросу. "
                        "Отвечай кратко, по делу, без лишней воды. "
                        "Если точных данных нет — предложи направления поиска: регионы, отрасли, сайты."
                    )},
                    {"role": "user", "content": text}
                ]
            )
            answer = completion.choices[0].message.content.strip()

            await update.message.reply_text(answer)
            save_dialog(uid, text, answer)

        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к ИИ: {e}")
        return

    # непонятный контекст
    await update.message.reply_text("Можете уточнить, что именно нужно найти? Например: 'поставщик диффузоров в Москве'.")

# === Запуск через Webhook (Render) ===
async def main():
    ensure_log_file_exists()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", greet_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # webhook для Render
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_URL')}/{BOT_TOKEN}"
    await app.bot.set_webhook(WEBHOOK_URL)

    print(f"🚀 Василий запущен! Webhook активен: {WEBHOOK_URL}")

    web_app = web.Application()
    web_app.router.add_post(f'/{BOT_TOKEN}', app.webhook_handler)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
