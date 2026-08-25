"""Runs student-submitted SQL against an isolated PostgreSQL database.

SAFETY MODEL (spec section 7)
------------------------------
Every submission - including its hidden-test check queries - runs
inside one transaction that is ALWAYS rolled back, never committed.
PostgreSQL supports transactional DDL (unlike MySQL), so this holds
even for a submission that runs CREATE TABLE, DROP TABLE, or DELETE:
none of it survives past the transaction, so the shared fixture data
(resources/sql/fixtures.sql) never needs re-provisioning between
submissions and can never be corrupted by one. A statement_timeout
bounds runaway queries the same way execution_service bounds Python
subprocesses.

This targets a disposable, developer-controlled Postgres instance (see
SQL_DATABASE_URL below) - never a shared/production database - the
same MVP security posture execution_service documents for the Python
sandbox: real isolation (a throwaway container, a rolled-back
transaction, a statement timeout), not a hardened multi-tenant sandbox.
"""

from __future__ import annotations

import os
import re
import time

import psycopg
from psycopg import sql as pg_sql

from app.domain.models import (
    SqlExercise,
    SqlHiddenTest,
    SqlSubmissionResult,
    TestOutcome,
)

_STATEMENT_TIMEOUT_MS = 5000
_MAX_PREVIEW_ROWS = 50

# Every submission already runs inside its own transaction that this
# module always rolls back (see below) - so a literal COMMIT/ROLLBACK/
# END/ABORT in student SQL isn't just useless, it's dangerous: COMMIT
# would permanently commit the ambient transaction (and everything the
# student did before it) to the SHARED fixture database, bypassing the
# rollback entirely. ROLLBACK TO SAVEPOINT is exempted - it's safe (see
# the SAVEPOINT used below) and needed for Transactions exercises.
#
# END/COMMIT/ROLLBACK/ABORT are only matched when they form a COMPLETE
# top-level statement on their own (anchored at a statement boundary,
# with nothing but an optional WORK/TRANSACTION before the next ``;``
# or end of string) - never mid-expression, so ordinary SQL like
# ``CASE ... END AS alias`` is never mistaken for a transaction-control
# statement.
_STRING_LITERAL_RE = re.compile(r"'(?:[^']|'')*'")
_DOLLAR_QUOTED_RE = re.compile(r"(\$\w*\$).*?\1", re.DOTALL)
_TXN_CONTROL_RE = re.compile(
    r"(?i)(?:^|;)\s*"
    r"(?:(commit|abort|end)|(rollback)(?!\s+to\b))"
    r"(?:\s+(?:work|transaction))?\s*(?:;|$)"
)


def _contains_transaction_control(query: str) -> bool:
    """True if ``query`` has a top-level COMMIT/ROLLBACK/END/ABORT.

    String literals and dollar-quoted bodies (PL/pgSQL function/
    procedure/trigger definitions, which legitimately end in ``END;``)
    are stripped first, so only a REAL top-level transaction-control
    statement matches.
    """
    stripped = _DOLLAR_QUOTED_RE.sub(" ", query)
    stripped = _STRING_LITERAL_RE.sub(" ", stripped)
    return bool(_TXN_CONTROL_RE.search(stripped))


# A local, developer-provisioned Postgres instance dedicated to grading
# SQL exercises (see scripts/provision_sql_fixtures.py) - overridable
# via env var for a different local setup, never a shared/production
# database.
SQL_DATABASE_URL = os.environ.get(
    "SQL_DATABASE_URL",
    "postgresql://postgres:pythongym@127.0.0.1:55432/python_gym_sql",
)


def _stringify_rows(rows: list[tuple]) -> list[list[str]]:
    """Convert arbitrary DB values (Decimal, date, None, ...) to strings
    for JSON transport - the API layer owns presentation, not psycopg
    types.
    """
    return [["" if v is None else str(v) for v in row] for row in rows]


def _compare(rows: list[list[str]], test: SqlHiddenTest, ordered: bool) -> TestOutcome:
    """Compare already-fetched, stringified ``rows`` against ``expected``."""
    label = test.label or "check"
    actual_rows = rows if ordered else sorted(rows)
    actual = repr(actual_rows)
    passed = actual == test.expected
    return TestOutcome(label=label, passed=passed, detail=repr(rows))


def _run_check(
    cur: psycopg.Cursor,
    test: SqlHiddenTest,
    student_rows: list[list[str]],
    student_error: str | None,
) -> TestOutcome:
    """Run one hidden test and compare its result against ``expected``.

    ``expect_error`` tests check that the student's OWN submitted query
    raised (``student_error``), not a separate query. Otherwise, a test
    with no ``check_query`` compares the student's own result
    (``student_rows``, already fetched and stringified) instead of
    running a separate query - see SqlHiddenTest.
    """
    label = test.label or "check"

    if test.expect_error:
        if student_error is not None:
            return TestOutcome(
                label=label, passed=True, detail=f"raised as expected: {student_error}"
            )
        return TestOutcome(
            label=label, passed=False, detail="expected an error, none raised"
        )

    if not test.check_query:
        return _compare(student_rows, test, ordered=test.ordered)

    try:
        cur.execute(test.check_query)
        rows = cur.fetchall()
    except psycopg.Error as exc:
        return TestOutcome(label=label, passed=False, detail=f"ERROR: {exc}")

    # check_query is required to be deterministic (an explicit ORDER
    # BY - see SqlHiddenTest), so its rows are always compared as-is.
    return _compare(_stringify_rows(rows), test, ordered=True)


def run_sql_submission(
    exercise: SqlExercise, student_query: str
) -> SqlSubmissionResult:
    """Execute ``student_query`` and every hidden test in one rolled-back
    transaction, and report a preview of the student's own result set
    alongside the pass/fail outcome of each hidden test.
    """
    start = time.perf_counter()
    tests: list[TestOutcome] = []
    preview_columns: list[str] = []
    preview_rows: list[list[str]] = []
    student_rows: list[list[str]] = []
    error: str | None = None

    if _contains_transaction_control(student_query):
        return SqlSubmissionResult(
            status="error",
            passed=False,
            tests_total=len(exercise.hidden_tests),
            tests_passed=0,
            tests=[],
            result_columns=[],
            result_rows=[],
            error=(
                "COMMIT, ROLLBACK, END, and ABORT aren't available in this "
                "practice sandbox - every exercise already runs inside its "
                "own transaction that's rolled back automatically when you "
                "submit, so there's nothing to commit or roll back "
                "yourself. Use SAVEPOINT and ROLLBACK TO SAVEPOINT instead "
                "if you need to undo part of your own submission."
            ),
            execution_time=time.perf_counter() - start,
        )

    try:
        with psycopg.connect(SQL_DATABASE_URL, autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    pg_sql.SQL("SET LOCAL statement_timeout = {}").format(
                        pg_sql.Literal(_STATEMENT_TIMEOUT_MS)
                    )
                )
                cur.execute("SET LOCAL search_path TO fixtures")
                # A savepoint lets a student query that raises (e.g. a
                # constraint violation an ``expect_error`` test wants)
                # be undone without aborting the whole transaction, so
                # hidden tests can still run afterwards.
                cur.execute("SAVEPOINT student_submission")
                try:
                    cur.execute(student_query)
                    if cur.description is not None:
                        preview_columns = [d.name for d in cur.description]
                        student_rows = _stringify_rows(cur.fetchall())
                        preview_rows = student_rows[:_MAX_PREVIEW_ROWS]
                except psycopg.Error as exc:
                    error = str(exc).strip()
                    cur.execute("ROLLBACK TO SAVEPOINT student_submission")

                for test in exercise.hidden_tests:
                    tests.append(_run_check(cur, test, student_rows, error))
            # Never commit - the fixture data must survive every
            # submission unchanged, whatever the student's query did.
            conn.rollback()
    except psycopg.OperationalError as exc:
        error = f"Could not reach the SQL grading database: {exc}"

    elapsed = time.perf_counter() - start
    tests_total = len(exercise.hidden_tests)
    tests_passed = sum(1 for t in tests if t.passed)
    all_passed = tests_total > 0 and tests_passed == tests_total

    if all_passed:
        status = "passed"
    elif error is not None:
        status = "error"
    else:
        status = "failed"

    return SqlSubmissionResult(
        status=status,
        passed=all_passed,
        tests_total=tests_total,
        tests_passed=tests_passed,
        tests=tests,
        result_columns=preview_columns,
        result_rows=preview_rows,
        error=error,
        execution_time=elapsed,
    )
