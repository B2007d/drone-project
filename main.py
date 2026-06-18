import asyncio
import logging
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, F, html
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command

# Вставь сюда токен от @BotFather
TOKEN = "8849138761:AAGCywW3sVYpJ3CMenJLfPqM90-Evp_Ft_w"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('digital_brain.db')
    cursor = conn.cursor()
    # Таблица для хранения любых мыслей и заметок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT,
            category TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

# Клавиатура для удобства
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧠 Мои воспоминания"), KeyboardButton(text="📊 Отчет за неделю")],
            [KeyboardButton(text="💡 Идеи бизнеса"), KeyboardButton(text="💰 Финансы")]
        ],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    init_db()
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! 🧠\n\n"
        f"Я — твой **Личный цифровой мозг**.\n"
        f"Отправляй мне любые мысли, идеи, траты или ссылки. "
        f"Я сохраню их навсегда и помогу найти в любой момент.\n\n"
        f"Используй поиск: просто напиши слово или нажми кнопки ниже.",
        reply_markup=get_main_keyboard()
    )

# Обработка входящих заметок
@dp.message(F.text & ~F.text.startswith('/') & ~F.text.in_({"🧠 Мои воспоминания", "📊 Отчет за неделю", "💡 Идеи бизнеса", "💰 Финансы"}))
async def save_memory(message: Message):
    user_id = message.from_user.id
    text = message.text
    
    # Базовая автоматическая категоризация по ключевым словам
    category = "Общее"
    text_lower = text.lower()
    if any(w in text_lower for w in ["купил", "потратил", "тенге", "руб", "$", "цена"]):
        category = "Финансы"
    elif any(w in text_lower for w in ["идея", "стартап", "бизнес", "проект"]):
        category = "Бизнес"
    elif any(w in text_lower for w in ["работа", "задача", "дело", "митинг"]):
        category = "Работа"

    # Сохраняем в БД
    conn = sqlite3.connect('digital_brain.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (user_id, content, category, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, text, category, datetime.now())
    )
    conn.commit()
    conn.close()

    await message.reply(f"📥 Запомнил в категорию **{category}**!")

# Простой поиск по кнопке "Мои воспоминания"
@dp.message(F.text == "🧠 Мои воспоминания")
async def show_memories(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('digital_brain.db')
    cursor = conn.cursor()
    cursor.execute("SELECT content, category FROM memories WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await message.answer("В твоем цифровом мозге пока пусто. Напиши мне что-нибудь!")
        return

    response = "🧠 **Последние 5 воспоминаний:**\n\n"
    for row in rows:
        response += f"• [{row[1]}] {row[0]}\n"
    await message.answer(response, parse_mode="Markdown")

# Поиск по ключевому слову (если пользователь ввел текст, которого нет в кнопках)
@dp.message(F.text)
async def search_memories(message: Message):
    user_id = message.from_user.id
    search_query = message.text

    conn = sqlite3.connect('digital_brain.db')
    cursor = conn.cursor()
    # Ищем совпадения по тексту
    cursor.execute(
        "SELECT content, timestamp FROM memories WHERE user_id = ? AND content LIKE ? ORDER BY timestamp DESC", 
        (user_id, f"%{search_query}%")
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await message.answer(f"🔍 По запросу «{search_query}» ничего не найдено.")
        return

    response = f"🔍 **Вот что я нашел по запросу «{search_query}»:**\n\n"
    for row in rows:
        date_str = row[1][:10] # Берём только дату YYYY-MM-DD
        response += f"📅 {date_str}: {row[0]}\n"
    await message.answer(response, parse_mode="Markdown")

async def main() -> None:
    init_db()
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
