"""SQLite connection handling and schema creation.

Kept intentionally simple (raw sqlite3, no ORM) since the goal of this
project is to learn Python, not to build a SaaS (spec section 6).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "python_gym.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    examples TEXT NOT NULL,
    starter_code TEXT NOT NULL,
    hints TEXT NOT NULL,           -- JSON list[str]
    expected_behavior TEXT NOT NULL,
    hidden_tests TEXT NOT NULL,    -- JSON list[{call, expected}]
    solution TEXT NOT NULL,
    explanation TEXT NOT NULL,
    concepts TEXT NOT NULL         -- JSON list[str]
);

CREATE TABLE IF NOT EXISTS progress (
    exercise_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'NEW',
    attempts INTEGER NOT NULL DEFAULT 0,
    hints_used INTEGER NOT NULL DEFAULT 0,
    solution_revealed INTEGER NOT NULL DEFAULT 0,
    last_submitted_at TEXT,
    FOREIGN KEY (exercise_id) REFERENCES exercises (id)
);

CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id TEXT NOT NULL,
    code TEXT NOT NULL,
    passed INTEGER NOT NULL,
    tests_total INTEGER NOT NULL,
    tests_passed INTEGER NOT NULL,
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (exercise_id) REFERENCES exercises (id)
);

CREATE TABLE IF NOT EXISTS explanations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (exercise_id) REFERENCES exercises (id)
);
"""


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with sensible defaults."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables if they do not already exist."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
