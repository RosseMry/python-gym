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
    hidden_tests TEXT NOT NULL,    -- JSON list[{call, expected, args, ...}]
    solution TEXT NOT NULL,
    explanation TEXT NOT NULL,
    concepts TEXT NOT NULL,        -- JSON list[str]
    -- Sprint 2 metadata (spec section 17):
    track TEXT NOT NULL DEFAULT 'python',
    source TEXT NOT NULL DEFAULT 'progressive_python',
    skills TEXT NOT NULL DEFAULT '[]',        -- JSON list[str]
    prerequisites TEXT NOT NULL DEFAULT '[]', -- JSON list[str]
    resources TEXT NOT NULL DEFAULT '[]',     -- JSON list[str]
    validation_profile TEXT NOT NULL DEFAULT 'standard_python',
    exercise_type TEXT NOT NULL DEFAULT 'function',
    exercise_status TEXT NOT NULL DEFAULT 'active',
    -- Sprint 3 correction: day/level within 30 Days of Python (NULL
    -- for every other source):
    day INTEGER,
    level INTEGER,
    -- Sprint 3 French translations, all optional (NULL = not
    -- translated yet, frontend falls back to the English field):
    title_fr TEXT,
    description_fr TEXT,
    examples_fr TEXT,
    expected_behavior_fr TEXT,
    explanation_fr TEXT,
    hints_fr TEXT,
    -- Sprint 3 finalization: optional per-hint Function Reference link,
    -- same length as hints - JSON list[str | None]:
    hint_functions TEXT
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
    status TEXT NOT NULL DEFAULT 'failed',
    hints_used_snapshot INTEGER NOT NULL DEFAULT 0,
    solution_revealed_snapshot INTEGER NOT NULL DEFAULT 0,
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

CREATE TABLE IF NOT EXISTS learning_notes (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    title TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    explanation TEXT NOT NULL,
    syntax TEXT NOT NULL,
    examples TEXT NOT NULL,
    common_mistakes TEXT NOT NULL,
    mini_exercise TEXT NOT NULL,
    related_exercise_ids TEXT NOT NULL DEFAULT '[]', -- JSON list[str]
    title_fr TEXT,
    explanation_fr TEXT,
    syntax_fr TEXT,
    examples_fr TEXT,
    common_mistakes_fr TEXT,
    mini_exercise_fr TEXT
);

CREATE TABLE IF NOT EXISTS sql_exercises (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    difficulty INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    starter_query TEXT NOT NULL,
    hints TEXT NOT NULL,           -- JSON list[str]
    expected_behavior TEXT NOT NULL,
    hidden_tests TEXT NOT NULL,    -- JSON list[{check_query, expected, ...}]
    solution TEXT NOT NULL,
    explanation TEXT NOT NULL,
    concepts TEXT NOT NULL DEFAULT '[]',
    skills TEXT NOT NULL DEFAULT '[]',
    source TEXT NOT NULL DEFAULT 'python_gym_sql',
    postgres_note TEXT,
    prerequisites TEXT NOT NULL DEFAULT '[]',
    exercise_status TEXT NOT NULL DEFAULT 'active',
    title_fr TEXT,
    description_fr TEXT,
    explanation_fr TEXT,
    hints_fr TEXT,
    schema TEXT NOT NULL DEFAULT 'fixtures',
    project TEXT,
    part INTEGER
);

CREATE TABLE IF NOT EXISTS sql_progress (
    exercise_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'NEW',
    attempts INTEGER NOT NULL DEFAULT 0,
    hints_used INTEGER NOT NULL DEFAULT 0,
    solution_revealed INTEGER NOT NULL DEFAULT 0,
    last_submitted_at TEXT,
    FOREIGN KEY (exercise_id) REFERENCES sql_exercises (id)
);

CREATE TABLE IF NOT EXISTS sql_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id TEXT NOT NULL,
    query TEXT NOT NULL,
    passed INTEGER NOT NULL,
    tests_total INTEGER NOT NULL,
    tests_passed INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'failed',
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (exercise_id) REFERENCES sql_exercises (id)
);

CREATE TABLE IF NOT EXISTS sql_learning_notes (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL,
    title TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    what_is_it TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    syntax TEXT NOT NULL,
    example TEXT NOT NULL,
    output TEXT NOT NULL,
    common_mistakes TEXT NOT NULL,
    mini_exercise TEXT NOT NULL,
    postgres_note TEXT,
    source TEXT NOT NULL DEFAULT 'freecodecamp',
    related_exercise_ids TEXT NOT NULL DEFAULT '[]',
    title_fr TEXT,
    what_is_it_fr TEXT,
    why_it_matters_fr TEXT,
    syntax_fr TEXT,
    common_mistakes_fr TEXT,
    mini_exercise_fr TEXT
);

CREATE TABLE IF NOT EXISTS exam_questions (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    category TEXT NOT NULL,
    prompt TEXT NOT NULL,
    difficulty INTEGER NOT NULL DEFAULT 1,
    points INTEGER NOT NULL DEFAULT 1,
    code_snippet TEXT,
    starter_code TEXT,
    choices TEXT,                  -- JSON list[str]
    correct_choice INTEGER,
    expected_output TEXT,
    hidden_tests TEXT,             -- JSON list[{call, expected, args, ...}]
    solution TEXT,
    explanation TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'adapted'
);

CREATE TABLE IF NOT EXISTS exam_sessions (
    id TEXT PRIMARY KEY,
    question_ids TEXT NOT NULL,    -- JSON list[str]
    started_at TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    deadline_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'in_progress',
    answers TEXT NOT NULL DEFAULT '{}',  -- JSON dict[str, str]
    submitted_at TEXT,
    score REAL,
    max_score REAL
);

CREATE TABLE IF NOT EXISTS function_references (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    what_it_does TEXT NOT NULL,
    syntax TEXT NOT NULL,
    parameters TEXT NOT NULL,
    return_value TEXT NOT NULL,
    example TEXT NOT NULL,
    example_output TEXT NOT NULL,
    common_mistakes TEXT NOT NULL,
    when_to_use TEXT NOT NULL,
    related_exercise_ids TEXT NOT NULL DEFAULT '[]', -- JSON list[str]
    name_fr TEXT,
    what_it_does_fr TEXT,
    parameters_fr TEXT,
    return_value_fr TEXT,
    common_mistakes_fr TEXT,
    when_to_use_fr TEXT
);
"""


# Columns added after the initial Sprint 1 release. CREATE TABLE IF NOT
# EXISTS does not retrofit columns onto an already-existing table, so an
# existing Sprint 1 database needs these added explicitly (Sprint 2).
_EXERCISE_MIGRATION_COLUMNS = {
    "track": "TEXT NOT NULL DEFAULT 'python'",
    "source": "TEXT NOT NULL DEFAULT 'progressive_python'",
    "skills": "TEXT NOT NULL DEFAULT '[]'",
    "prerequisites": "TEXT NOT NULL DEFAULT '[]'",
    "resources": "TEXT NOT NULL DEFAULT '[]'",
    "validation_profile": "TEXT NOT NULL DEFAULT 'standard_python'",
    "exercise_type": "TEXT NOT NULL DEFAULT 'function'",
    "exercise_status": "TEXT NOT NULL DEFAULT 'active'",
    "day": "INTEGER",
    "level": "INTEGER",
    # Sprint 3 French translations - see app.domain.models.Exercise.
    "title_fr": "TEXT",
    "description_fr": "TEXT",
    "examples_fr": "TEXT",
    "expected_behavior_fr": "TEXT",
    "explanation_fr": "TEXT",
    "hints_fr": "TEXT",
    "hint_functions": "TEXT",
}

_SQL_EXERCISE_MIGRATION_COLUMNS = {
    # SQL content reorganization (Sprint 4 Mini Project prep) - see
    # app.domain.models.SqlExercise's docstring.
    "schema": "TEXT NOT NULL DEFAULT 'fixtures'",
    "project": "TEXT",
    "part": "INTEGER",
}

_SUBMISSION_MIGRATION_COLUMNS = {
    "status": "TEXT NOT NULL DEFAULT 'failed'",
    "hints_used_snapshot": "INTEGER NOT NULL DEFAULT 0",
    "solution_revealed_snapshot": "INTEGER NOT NULL DEFAULT 0",
}


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with sensible defaults.

    check_same_thread=False: FastAPI resolves a sync Depends() and the
    sync endpoint it feeds via separate run_in_threadpool calls, which
    can land on different worker threads for the same request. The
    connection here is still request-scoped (never shared across
    concurrent requests), so relaxing this check is safe.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate_columns(
    conn: sqlite3.Connection, table: str, columns: dict[str, str]
) -> None:
    """Add any missing columns from ``columns`` to an existing table."""
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
    for column, ddl in columns.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
    conn.commit()


def init_db() -> None:
    """Create tables if they do not already exist, and migrate old ones."""
    conn = get_connection()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _migrate_columns(conn, "exercises", _EXERCISE_MIGRATION_COLUMNS)
        _migrate_columns(conn, "submissions", _SUBMISSION_MIGRATION_COLUMNS)
        _migrate_columns(conn, "sql_exercises", _SQL_EXERCISE_MIGRATION_COLUMNS)
    finally:
        conn.close()
