import os
from openai import OpenAI
import openai
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
ALLOWED_USERS = {7299174753}  # ← замени на свой Telegram ID
BOT_NAME = "василий"

# === Приветствие ===
async def greet_user(update, context):
    await update.message.reply_text("Привет! Меня зовут Василий 👋 Какого поставщика найти для тебя?")
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
        {"role": "system", "content": "Ты помощник HVAC-компании. Помогаешь искать производителей и поставщиков вентиляционного и климатического оборудования."},
        {"role": "user", "content": text}
    ]
)
answer = completion.choices[0].message.content
await update.message.reply_text(answer)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к ИИ: {e}")
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
