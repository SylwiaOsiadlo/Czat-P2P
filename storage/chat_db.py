import sqlite3
from pathlib import Path

# Ścieżka do bazy danych
db_path = Path("chat_database.sqlite")

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS active_users (
        username TEXT UNIQUE NOT NULL,
        port INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def save_message(sender: str, content: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, content) VALUES (?, ?)", (sender, content))
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT sender, content, timestamp FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    messages = c.fetchall()
    conn.close()
    return messages[::-1]

def add_user(username: str, password_hash: str) -> bool:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def validate_user(username: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user:
        return (user[0], None)
    return None

def set_user_active(username: str, port: int):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("REPLACE INTO active_users (username, port) VALUES (?, ?)", (username, port))
    conn.commit()
    conn.close()

def get_active_users():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT username, port FROM active_users")
    users = c.fetchall()
    conn.close()
    return users

def set_user_inactive(username: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM active_users WHERE username = ?", (username,))
    conn.commit()
    conn.close()