"""
Telegram-бот шаблон (aiogram 3.x + SQLite)
Готовый каркас: приём заявок, БД, уведомления админу, админ-панель.

Запуск:
    pip install aiogram aiosqlite
    # создай .env: BOT_TOKEN=твой_токен  ADMIN_ID=твой_id
    python bot.py

Логика:
    /start -> главное меню
    "Оставить заявку" -> пользователь вводит текст -> сохраняется в БД -> админу приходит уведомление
    /admin -> список последних заявок (только для ADMIN_ID)
"""

import asyncio
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB_PATH = "bot.db"

# ---------- База данных ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            text TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_request(user_id: int, username: str, text: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO requests (user_id, username, text, created_at) VALUES (?, ?, ?, ?)",
        (user_id, username, text, datetime.now().strftime("%Y-%m-%d %H:%M")),
    )
    conn.commit()
    conn.close()

def get_recent_requests(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, username, text, created_at FROM requests ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------- Состояния (FSM) ----------
class RequestForm(StatesGroup):
    waiting_text = State()

# ---------- Клавиатура ----------
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Оставить заявку")],
        [KeyboardButton(text="ℹ️ О нас")],
    ],
    resize_keyboard=True,
)

# ---------- Хэндлеры ----------
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Это шаблон бота.\n"
        "Нажми «Оставить заявку» — мы получим твоё сообщение.",
        reply_markup=main_kb,
    )

async def cmd_about(message: Message):
    await message.answer("Это демо-бот на aiogram. Замени тексты под свой бизнес.")

async def btn_request(message: Message, state: FSMContext):
    await state.set_state(RequestForm.waiting_text)
    await message.answer("✍️ Напиши свою заявку (что нужно сделать):")

async def process_request(message: Message, state: FSMContext):
    text = message.text
    save_request(message.from_user.id, message.from_user.username or "нет", text)
    # уведомление админу
    if ADMIN_ID:
        try:
            await message.bot.send_message(
                ADMIN_ID,
                f"🔔 Новая заявка #{message.from_user.id}\n"
                f"От: @{message.from_user.username or 'нет'}\n"
                f"Текст: {text}",
            )
        except Exception:
            pass
    await state.clear()
    await message.answer("✅ Заявка отправлена! Мы свяжемся с тобой.", reply_markup=main_kb)

async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    rows = get_recent_requests(10)
    if not rows:
        await message.answer("Заявок пока нет.")
        return
    text = "📋 Последние заявки:\n\n"
    for r in rows:
        text += f"#{r[0]} | @{r[1]} | {r[3]}\n{r[2]}\n——\n"
    await message.answer(text)

# ---------- Точка входа ----------
async def main():
    if not BOT_TOKEN:
        raise SystemExit("❌ Не задан BOT_TOKEN в .env")
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_admin, Command("admin"))
    dp.message.register(btn_request, F.text == "📝 Оставить заявку")
    dp.message.register(cmd_about, F.text == "ℹ️ О нас")
    dp.message.register(process_request, RequestForm.waiting_text)
    print("Бот запущен. Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
