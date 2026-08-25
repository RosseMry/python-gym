"""Loads the SQL exercise fixture schema/data into the Postgres instance
used for grading (spec section 8).

Run with:

    uv run python scripts/provision_sql_fixtures.py

Idempotent - drops and recreates the "fixtures" schema each time, so
it's safe to rerun after editing resources/sql/fixtures.sql. This is
the only script in Sprint 4 that runs DDL/DML directly against the
grading database outside a rolled-back transaction, since it is
provisioning the fixture data itself, not grading a student submission.
"""

from __future__ import annotations

import sys
from pathlib import Path

import psycopg

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services.sql_execution_service import SQL_DATABASE_URL  # noqa: E402

FIXTURES_SQL_PATH = BACKEND_DIR.parent / "resources" / "sql" / "fixtures.sql"


def main() -> None:
    sql = FIXTURES_SQL_PATH.read_text(encoding="utf-8")
    with psycopg.connect(SQL_DATABASE_URL, autocommit=True) as conn:
        conn.execute(sql)
    relative_path = FIXTURES_SQL_PATH.relative_to(BACKEND_DIR.parent)
    print(f"Provisioned fixtures schema from {relative_path}")


if __name__ == "__main__":
    main()
