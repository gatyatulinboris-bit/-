import os
import json
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== Конфигурация =====
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = 7299174753  # доступ только тебе
DIALOG_FILE = "dialog_history.json"
SUPPLIERS_FILE = "suppliers.json"
DAYS_TO_KEEP = 30

def ensure_file(path: str, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

def update_suppliers_seed():
    ensure_file(SUPPLIERS_FILE, [])
    with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        data.extend([
            {"name": "СтройМаркет", "category": "цемент",     "region": "Москва",        "contact": "stroymarket.ru"},
            {"name": "БетонСнаб",   "category": "бетон",      "region": "Санкт-Петербург","contact": "betonsnab.ru"},
            {"name": "АрмаРус",     "category": "арматура",   "region": "Екатеринбург",  "contact": "armarus.ru"},
            {"name": "КирпичПроф",  "category": "кирпич",     "region": "Казань",        "contact": "kirpichprof.ru"},
            {"name": "ТехСтрой",    "category": "сухие смеси","region": "Новосибирск",   "contact": "tehstroi.ru"}
        ])
        with open(SUPPLIERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def save_dialog(user_id: int, text: str, reply: str):
    ensure_file(DIALOG_FILE, [])
    # читаем
    try:
        with open(DIALOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []
    # чистим старые
    cutoff = datetime.now() - timedelta(days=DAYS_TO_KEEP)
    data = [
        d for d in data
        if datetime.strptime(d.get("timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S") >= cutoff
    ]
    # добавляем новую запись
    data.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "text": text,
        "reply": reply
    })
    with open(DIALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_suppliers(query: str):
    with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
        suppliers = json.load(f)
    q = query.lower()
    # простое совпадение по категории
    found = [s for s in suppliers if s["category"] in q]
    return found[:3]

# === Хендлеры ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Доступ запрещён. Обратитесь к администратору.")
        return
    msg = ("Здравствуйте! Я Василий — помощник по поиску строительных поставщиков в России.\n"
           "Что именно нужно найти? Укажите категорию и регион (например: «цемент Москва»).")
    await update.message.reply_text(msg)

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    if user_id != ADMIN_ID:
        await update.message.reply_text("🚫 У вас нет доступа к этому боту.")
        return

    print(f"[LOG] Запрос от {user_id}: {text}")
    results = find_suppliers(text)
    if results:
        reply = "Нашёл поставщиков:\n\n" + "\n".join(
            [f"🏗 {s['name']} — {s['category']} ({s['region']})\n🌐 {s['contact']}" for s in results]
        )
    else:
        reply = "Пока не нашёл. Добавляю кандидата в базу и продолжу накапливать варианты."
        # добавим «черновой» элемент под запрос
        ensure_file(SUPPLIERS_FILE, [])
        with open(SUPPLIERS_FILE, "r+", encoding="utf-8") as f:
            arr = json.load(f)
            arr.append({
                "name": f"Новый поставщик {len(arr)+1}",
                "category": text.lower(),
                "region": "Россия",
                "contact": "—"
            })
            f.seek(0); json.dump(arr, f, ensure_ascii=False, indent=2); f.truncate()

    await update.message.reply_text(reply)
    save_dialog(user_id, text, reply)

# === Запуск (Long Polling, без вебхуков) ===
async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не задан в Environment Variables.")
    update_suppliers_seed()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    print("🤖 Василий запущен. Ожидаю запросы (long polling)…")
    await app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())
