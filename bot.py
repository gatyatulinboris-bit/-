import os
from openai import OpenAI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Конфигурация ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Добавь свой Telegram ID, чтобы ограничить доступ
ALLOWED_USERS = {7299174753}  # ← замени на свой ID
BOT_NAME = "василий"

# === Глобальная память диалога ===
conversation_history = []  # хранит последние 10 сообщений

# === Приветствие ===
async def greet_user(update, context):
    await update.message.reply_text(
        "Привет! Меня зовут Василий 👋\n"
        "Помогаю искать производителей и поставщиков HVAC-оборудования.\n"
        "Что нужно найти?"
    )

# === Основная логика общения ===
a
