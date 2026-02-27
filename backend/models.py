import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """정적 테이블은 Google Sheets로 이전됨. 아무 작업도 수행하지 않음."""
    pass
