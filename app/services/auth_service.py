import sqlite3
import time
from typing import Optional, List, Dict
from app.database import DB_PATH
from app.core.security import get_password_hash, verify_password, create_access_token


def init_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 1,
            created_at INTEGER
        )
    """)
    conn.commit()
    conn.close()


def create_default_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        password_hash = get_password_hash("admin123")
        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO users (username, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?)
        """, ("admin", password_hash, 1, timestamp))
        conn.commit()
        print("Usuario admin creado: username='admin', password='admin123'")
    conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def create_user(username: str, password: str, is_admin: bool = True) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = get_password_hash(password)
        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO users (username, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, 1 if is_admin else 0, timestamp))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
