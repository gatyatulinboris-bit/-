import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Твой токен подтягивается из переменных окружения (мы добавим его на Render) ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Белый список пользователей (добавь свой Telegram ID) ===
ALLOWED_USERS = {7299174753}  # ← замени на свой ID, полученный через @userinfobot

# === Команда /start или “Васили Привет!” ===
async def start(update, context):
    uid = update.effective_user.id

    # Проверяем, что пользователь разрешён
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ только по приглашению.")
        return

    user_name = update.effective_user.first_name or "друг"
    await update.message.reply_text(
        f"Привет, {user_name}! 👋\n"
        "Я твой помощник по поиску поставщиков.\n"
        "Напиши, что нужно найти, например:\n\n"
        "🔍 Найди мне поставщика огнезащитного покрытия для воздуховодов EI150."
    )

# === Логика ответов (пока без ИИ) ===
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # Ограничение доступа
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return

    # Если пользователь пишет “Васили Привет” — отрабатываем как старт
    if text.lower().startswith("васили привет"):
        await start(update, context)
        return

    # Пример обработки запроса
    if "найди" in text.lower() and "поставщик" in text.lower():
        await update.message.reply_text(
            "🔍 Ищу поставщиков по вашему запросу...\n"
            "⏳ (пока заглушка — позже подключим ИИ и реальный поиск)"
        )
        return

    # Всё остальное — эхо
    await update.message.reply_text(f"Ты написал: {text}")

# === Основной запуск ===
def main():
    if not BOT_TOKEN:
        raise SystemExit("Не найден BOT_TOKEN — добавь его в Environment Variables.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Бот запущен и ждёт сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()
