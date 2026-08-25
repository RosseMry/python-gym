"""Loads every SQL fixture file's schema/data into the Postgres
instance used for grading (spec section 8).

Run with:

    uv run python scripts/provision_sql_fixtures.py

Idempotent - each resources/sql/*.sql file drops and recreates its own
named schema (DROP SCHEMA IF EXISTS ... CASCADE), so it's safe to
rerun after editing any of them. Every *.sql file under resources/sql/
is provisioned - the Foundations/JOINs/... "fixtures" schema
(fixtures.sql) and a Mini Project's own dedicated dataset (e.g.
ecommerce_fixtures.sql) alike - so adding a new Mini Project's fixture
file needs no change here (see SqlExercise.schema's docstring for why
a Mini Project gets its own schema rather than sharing "fixtures").

This is the only script in Sprint 4 that runs DDL/DML directly against
the grading database outside a rolled-back transaction, since it is
provisioning the fixture data itself, not grading a student submission.
"""

from __future__ import annotations

import sys
from pathlib import Path

import psycopg

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services.sql_execution_service import SQL_DATABASE_URL  # noqa: E402

FIXTURES_DIR = BACKEND_DIR.parent / "resources" / "sql"


def main() -> None:
    sql_files = sorted(FIXTURES_DIR.glob("*.sql"))
    if not sql_files:
        print(f"No SQL fixture files found under {FIXTURES_DIR}")
        return

    with psycopg.connect(SQL_DATABASE_URL, autocommit=True) as conn:
        for path in sql_files:
            conn.execute(path.read_text(encoding="utf-8"))
            relative_path = path.relative_to(BACKEND_DIR.parent)
            print(f"Provisioned schema from {relative_path}")


if __name__ == "__main__":
    main()
