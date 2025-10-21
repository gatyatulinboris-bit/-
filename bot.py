import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Твой токен подтягивается из переменных окружения (мы добавим его на Render) ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Белый список пользователей (добавь свой Telegram ID) ===
ALLOWED_USERS = {7299174753}  # ← замени на свой ID, полученный через @userinfobot

# === Имя бота ===
BOT_NAME = "василий"

# === Приветствие ===
async def greet_user(update, context):
    """Обрабатывает /start или фразу 'Василий Привет'."""
    uid = update.effective_user.id
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ только по приглашению.")
        return

    await update.message.reply_text(
        "Привет! Меня зовут Василий 👋\n"
        "Какого поставщика найти для тебя?"
    )

# === Основной обработчик сообщений ===
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip().lower()

    # Проверка доступа
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return

    # Если пользователь написал 'Василий привет' → приветствие
    if text.startswith(f"{BOT_NAME} привет"):
        await greet_user(update, context)
        return

    # Если пользователь просит найти поставщика
    if "найди" in text and "постав" in text:
        await update.message.reply_text(
            f"🔍 Ищу поставщиков по запросу:\n«{update.message.text}»\n"
            "⏳ (пока заглушка — позже подключим ИИ и реальный поиск)"
        )
        return

    # Всё остальное — эхо
    await update.message.reply_text(f"Ты написал: {update.message.text}")
