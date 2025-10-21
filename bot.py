import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Токен НЕ храним в коде. Передадим его как переменную окружения на Render.
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Разрешённые пользователи: подставь свой Telegram ID (узнать через @userinfobot)
ALLOWED_USERS = {8396494240}

async def start(update, context):
    uid = update.effective_user.id
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ только по приглашению.")
        return
    await update.message.reply_text("Привет! Я онлайн в облаке. Напиши что-нибудь.")

async def echo(update, context):
    uid = update.effective_user.id
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return
    await update.message.reply_text(f"Ты написал: {update.message.text}")

def main():
    if not BOT_TOKEN:
        raise SystemExit("Не найден BOT_TOKEN (добавь на Render в Environment Variables)")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()

if __name__ == "__main__":
    main()
