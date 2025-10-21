import os
from openai import OpenAI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Конфигурация ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ALLOWED_USERS = {7299174753}  # ← замени на свой Telegram ID
BOT_NAME = "василий"

# === Приветствие ===
async def greet_user(update, context):
    await update.message.reply_text(
        "Привет! Меня зовут Василий 👋 Какого поставщика найти для тебя?"
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

    if "найди" in text.lower() or "постав" in text.lower():
        await update.message.reply_text("🤖 Думаю над ответом...")
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — Василий, помощник HVAC-компании. "
                            "Помогаешь находить производителей, поставщиков и дилеров "
                            "вентиляционного, климатического и автоматизационного оборудования. "
                            "Отвечай профессионально и по существу."
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

    # Если нет ключевых слов
    await update.message.reply_text(f"Ты написал: {text}")

# === Основной запуск ===
def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден!")
        return

    print("✅ Василий запускается...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", greet_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Василий запущен и ждёт сообщений...")
    app.run_polling()  # держит процесс активным

if __name__ == "__main__":
    main()
