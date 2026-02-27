import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """정적 참조 테이블만 생성 (동적 데이터는 Google Sheets로 관리)."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS competency_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sub_category TEXT
        );

        CREATE TABLE IF NOT EXISTS competencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL REFERENCES competency_groups(id),
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL REFERENCES competency_groups(id),
            situation TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scenario_competencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
            competency_id INTEGER NOT NULL REFERENCES competencies(id)
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competency_id INTEGER NOT NULL REFERENCES competencies(id),
            name TEXT NOT NULL,
            description TEXT,
            duration_hours INTEGER,
            semester TEXT
        );
    ''')
    conn.commit()
    conn.close()
