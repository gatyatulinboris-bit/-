import os
import json
import logging
from datetime import datetime, timedelta
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

client = OpenAI(api_key=OPENAI_API_KEY)
ALLOWED_USERS = {7299174753}  # ← твой Telegram ID
LOG_FILE = "dialog_history.json"
DAYS_TO_KEEP = 30  # храним диалоги 30 дней


# === Проверка и создание файла истории ===
def ensure_log_file_exists():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print("[INFO] Файл истории создан.")
    else:
        print("[INFO] Файл истории найден.")


# === Сохранение истории ===
def save_dialog(user_id, message, reply):
    now = datetime.now()
    cutoff = now - timedelta(days=DAYS_TO_KEEP)
    data = []

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

    data = [
        d for d in data
        if datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S") >= cutoff
    ]

    data.append({
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "message": message,
        "reply": reply
    })

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я Василий 🤖 — помощник по поиску поставщиков и производителей в России.\n"
        "Что нужно найти?"
    )


# === Основная логика ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 У вас нет доступа к Василию.")
        return

    await update.message.reply_text("🤖 Думаю над ответом...")

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "Ты — Василий, умный ассистент по закупкам в России. "
                    "Ты ищешь и предлагаешь 2–3 реальных варианта поставщиков или производителей по запросу."
                )},
                {"role": "user", "content": text}
            ]
        )
        answer = completion.choices[0].message.content.strip()

        await update.message.reply_text(answer)
        save_dialog(uid, text, answer)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")


# === Проверка webhook ===
async def check_webhook(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            info = await response.json()
            print(f"[DEBUG] Текущее состояние webhook:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return info


# === Запуск ===
async def main():
    ensure_log_file_exists()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    webhook_url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
    print(f"[BOOT] Устанавливаю webhook: {webhook_url}")

    try:
        await app.bot.set_webhook(url=webhook_url)
        info = await check_webhook(BOT_TOKEN)

        if info.get("ok") and info["result"].get("url") == webhook_url:
            print(f"[OK] Webhook успешно установлен ✅")
        else:
            print(f"[WARN] Webhook не совпадает или не установлен корректно ⚠️")
            print(json.dumps(info, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"[ERROR] Не удалось установить webhook: {e}")

    print("🤖 Василий запущен, ожидаю сообщения...")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        url_path=BOT_TOKEN,
        webhook_url=webhook_url
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
