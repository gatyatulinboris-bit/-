import os
from openai import OpenAI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_USERS = {7299174753}  # ← замени на свой Telegram ID
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
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # Проверяем доступ
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return

    # Если пользователь просто здоровается
    if text.lower().startswith(f"{BOT_NAME} привет"):
        await greet_user(update, context)
        return

    # Если сообщение связано с поиском или поставкой
    if "найди" in text.lower() or "постав" in text.lower():
        await update.message.reply_text("🤖 Думаю над ответом...")

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты помощник HVAC-компании. "
                            "Помогаешь искать производителей и поставщиков "
                            "вентиляционного и климатического оборудования."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
            )

            answer = completion.choices[0].message.content
            await update.message.reply_text(answer)

        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к ИИ: {e}")
        return

    # Если ничего не подошло — нейтральный ответ
    if not any(word in text.lower() for word in ["найди", "постав", "закажи", "ищу"]):
        # Василий просто молчит или отвечает мягко
        await update.message.reply_text("🧩 Я тебя услышал, думаю, чем могу помочь.")


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
    app.run_polling()  # ← обязательная строка для постоянной работы


if __name__ == "__main__":
    main()
