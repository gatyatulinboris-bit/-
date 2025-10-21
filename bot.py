import os
import json
from datetime import datetime, timedelta
from openai import OpenAI
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# === Настройки ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ALLOWED_USERS = {7299174753}  # ← твой Telegram ID
BOT_NAME = "василий"
LOG_FILE = "dialog_history.json"
DAYS_TO_KEEP = 30  # храним диалоги 30 дней

# === Проверка и создание файла истории при запуске ===
def ensure_log_file_exists():
    """Создает пустой файл истории, если его нет"""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print("[INFO] Файл истории диалогов не найден — создан новый dialog_history.json")
    else:
        print("[INFO] Файл истории диалогов найден ✅")


# === Загрузка и сохранение истории ===
def save_dialog(user_id, message, reply):
    """Сохраняет сообщение и очищает старые записи старше DAYS_TO_KEEP"""
    data = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=DAYS_TO_KEEP)

    # Загружаем старые диалоги
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    # Фильтруем только свежие записи
    filtered_data = []
    for entry in data:
        try:
            entry_time = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
            if entry_time >= cutoff_date:
                filtered_data.append(entry)
        except Exception:
            continue

    # Добавляем новое сообщение
    filtered_data.append({
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "message": message,
        "reply": reply
    })

    # Перезаписываем файл
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)


# === Приветствие ===
async def greet_user(update, context):
    await update.message.reply_text(
        "Здравствуйте! Я Василий — помощник по поиску поставщиков и производителей в России 🇷🇺.\n"
        "Помогаю находить надёжных партнёров в строительстве, HVAC, автопроме, продуктах, одежде и других сферах.\n\n"
        "Что именно нужно найти?"
    )


# === Основная логика общения ===
async def handle_message(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # Проверяем доступ
    if uid not in ALLOWED_USERS:
        await update.message.reply_text("🚫 У вас нет доступа к Василию.")
        return

    # Если пользователь просто здоровается
    if any(word in text.lower() for word in ["привет", "здравствуй", "добрый день", "хай"]):
        await update.message.reply_text("Здравствуйте 👋 Я Василий. Что нужно найти?")
        return

    # Если запрос похож на поиск
    if any(word in text.lower() for word in ["найди", "ищи", "поставщик", "производитель", "где купить", "закупка", "купить", "искать"]):
        await update.message.reply_text("🤖 Думаю над ответом, подбираю варианты...")

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": (
                        "Ты — Василий, умный ассистент по закупкам в России. "
                        "Ты ищешь и предлагаешь 2–3 реальных варианта поставщиков или производителей по запросу. "
                        "Отвечай кратко, по делу, без лишней воды. "
                        "Если точных данных нет, предложи логичные направления поиска: регионы, категории компаний, отрасли."
                    )},
                    {"role": "user", "content": text}
                ]
            )
            answer = completion.choices[0].message.content.strip()

            await update.message.reply_text(answer)
            save_dialog(uid, text, answer)

        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при обращении к ИИ: {e}")
        return

    # Если Василий не понял контекст
    await update.message.reply_text("Можете уточнить, что именно нужно найти? Например: 'поставщик диффузоров в Москве'.")


# === Запуск ===
def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден!")
        return

    ensure_log_file_exists()  # Проверяем или создаём файл истории

    print("✅ Василий запускается...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", greet_user))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Василий запущен и ждёт сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()
