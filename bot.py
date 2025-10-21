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


# === Работа с памятью ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === Инициализация памяти ===
memory = load_memory()
if "stage" not in memory:
    memory["stage"] = "start"
if "history" not in memory:
    memory["history"] = []


# === Приветствие ===
async def greet_user(update, context):
    memory["stage"] = "greeting"
    save_memory(memory)
    await update.message.reply_text(
        "Здравствуйте. Василий — помощник по вентиляции и кондиционированию.\n"
        "Помогаю находить поставщиков, производителей и оборудование.\n"
        "Что именно нужно подобрать?"
    )


# === Основная логика ===
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # Проверка доступа
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Доступ закрыт.")
        return

    stage = memory.get("stage", "start")

    # Этап 1: Приветствие
    if stage == "start" or "привет" in text.lower():
        await greet_user(update, context)
        return

    # Этап 2: Определяем запрос
    if stage == "greeting":
        memory["request"] = text
        memory["stage"] = "searching"
        save_memory(memory)
        await update.message.reply_text("Принял. Сейчас подберу поставщиков...")

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "Ты — помощник HVAC-компании. "
                        "Отвечай делово, по существу. "
                        "Найди известных производителей или поставщиков по теме запроса. "
                        "Формат ответа: список из 3–5 пунктов с краткими комментариями."
                    )},
                    {"role": "user", "content": text},
                ],
            )

            answer = completion.choices[0].message.content
            memory["answer"] = answer
            memory["stage"] = "confirm"
            save_memory(memory)

            await update.message.reply_text(answer)
            await update.message.reply_text("Это то, что вы искали, или уточнить направление?")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при поиске: {e}")
        return

    # Этап 3: Подтверждение
    if stage == "confirm":
        if any(word in text.lower() for word in ["да", "верно", "подходит", "отлично", "спасибо"]):
            await update.message.reply_text("Хорошо. Рад был помочь. Если потребуется расчёт или подбор — обращайтесь.")
            memory["stage"] = "done"
            save_memory(memory)
            return
        else:
            memory["stage"] = "searching"
            save_memory(memory)
            await update.message.reply_text("Уточните, пожалуйста, что именно нужно — я скорректирую подбор.")
            return

    # Этап 4: Завершение
    if stage == "done":
        await update.message.reply_text("Если нужно будет что-то ещё — пишите, я на связи.")
        memory["stage"] = "start"
        save_memory(memory)
        return


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
    app.run_polling()


if __name__ == "__main__":
    main()
