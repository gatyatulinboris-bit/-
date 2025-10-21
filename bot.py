import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USERS = {7299174753}  # ← замени на свой Telegram ID
BOT_NAME = "василий"

# === Приветствие ===
async def greet_user(update, context):
    uid = update.effective_user.id
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ только по приглашению.")
        return

    await update.message.reply_text(
        "Привет! Меня зовут Василий 👋\n"
        "Какого поставщика найти для тебя?"
    )

# === Обработка сообщений ===
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return

    if text.lower().startswith(f"{BOT_NAME} привет"):
        await greet_user(update, context)
        return

    if "найди" in text.lower() and "постав" in text.lower():
        await update.message.reply_text(
            f"🔍 Ищу поставщиков по запросу:\n«{text}»\n"
            "⏳ (пока заглушка — позже подключим ИИ)"
        )
        return

    await update.message.reply_text(f"Ты написал: {text}")

# === Запуск ===
def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден!")
        return

    print("✅ Василий запускается...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", greet_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Василий запущен и ждёт сообщений...")
    app.run_polling()  # — эта строка держит процесс в режиме ожидания

if __name__ == "__main__":
    main()
