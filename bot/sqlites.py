import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "bot" / "telegram_users.db"

async def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS T_Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            name TEXT,
            chat_id INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


async def reg_user(data: dict, chat_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO T_Users (email, name, chat_id)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO NOTHING
    ''', (data["email"], data["name"], chat_id))
    conn.commit()
    conn.close()