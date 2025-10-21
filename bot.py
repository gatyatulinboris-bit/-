import os
import json
from openai import OpenAI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_USERS = {7299174753}  # ← замени на свой Telegram ID
BOT_NAME = "василий"
MEMORY_FILE = "memory.json"  # файл для хранения памяти


# === Функции для работы с памятью ===
def load_memory():
    """Загрузка истории из файла"""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_memory(history):
    """Сохранение истории в файл"""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)  # храним последние 10 сообщений


# === Глобальная память ===
conversation_history = load_memory()


# === Приветствие ===
async def greet_user(update, context):
    await update.message.reply_text(
        "Привет! Меня зовут Василий 👋\n"
        "Помогаю искать производителей и поставщиков HVAC-оборудования.\n"
        "Что нужно найти?"
    )


# === Основная логика общения ===
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # Проверяем доступ
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return

    # Приветствие
    if text.lower().startswith(f"{BOT_NAME} привет"):
        await greet_user(update, context)
        return

    # Добавляем сообщение пользователя в память
    conversation_history.append({"role": "user", "content": text})
    save_memory(conversation_history)

    # Проверяем запросы по ключевым словам
    if "найди" in text.lower() or "постав" in text.lower():
        await update.message.reply_text("🤖 Думаю над ответом...")

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "Ты помощник HVAC-компании. "
                        "Помогаешь искать производителей и поставщиков вентиляционного и климатического оборудования."
                    )},
                    *conversation_history[-10:],  # подгружаем последние 10 сообщений
                ],
            )

            answer = completion.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": answer})
            save_memory(conversation_history)

            await update.message.reply_text(answer)

        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к ИИ: {e}")

        return

    # Если текст не подходит под ключевые слова
    await update.message.reply_text("🧩 Я тебя услышал, подумаю, как помочь.")


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
    app.run_polling()  # держит бота в работе


if __name__ == "__main__":
    main()
