"""Tests for the SQL exercise content under sql_exercises/ (Sprint 4).

Mirrors test_seed_content.py's pattern for the Python content: load
every file through the real seed mechanism and assert on the actual
loaded data, never on hand-copied numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import SqlExercise  # noqa: E402
from scripts.seed_sql import EXERCISES_DIR, load_exercise  # noqa: E402

EXPECTED_MODULE_COUNTS = {
    "foundations": 14,
    "relational": 4,
    "joins": 6,
    "intermediate": 8,
    "window": 6,
    "dbops": 8,
    "views": 3,
    "transactions": 3,
    "indexes": 3,
    "functions": 3,
    "procedures": 2,
    "triggers": 2,
}


@pytest.fixture(scope="module")
def exercises() -> list[SqlExercise]:
    paths = sorted(EXERCISES_DIR.glob("**/*.json"))
    assert paths, f"no SQL exercise files found under {EXERCISES_DIR}"
    return [load_exercise(p) for p in paths]


def test_no_duplicate_ids(exercises: list[SqlExercise]) -> None:
    ids = [e.id for e in exercises]
    assert len(ids) == len(set(ids)), "duplicate SQL exercise id"


def test_module_counts_match_expectations(exercises: list[SqlExercise]) -> None:
    by_module: dict[str, int] = {}
    for e in exercises:
        by_module[e.module] = by_module.get(e.module, 0) + 1
    for module, expected_count in EXPECTED_MODULE_COUNTS.items():
        assert by_module.get(module) == expected_count, module


def test_id_prefix_matches_module(exercises: list[SqlExercise]) -> None:
    for e in exercises:
        assert e.id.startswith(f"sql-{e.module}-"), e.id


def test_every_exercise_has_three_hints(exercises: list[SqlExercise]) -> None:
    for e in exercises:
        assert len(e.hints) == 3, e.id
        assert e.hints[0].startswith("\U0001F4A1"), e.id  # the 💡 marker


def test_every_exercise_has_at_least_one_hidden_test(
    exercises: list[SqlExercise],
) -> None:
    for e in exercises:
        assert len(e.hidden_tests) >= 1, e.id


def test_hints_never_leak_the_literal_solution(exercises: list[SqlExercise]) -> None:
    """No hint may contain the full solution query verbatim - prose that
    explains what the query does is fine, a copy-pasted answer is not.
    """
    for e in exercises:
        solution = e.solution.strip()
        for hint in e.hints:
            assert solution not in hint, (e.id, hint)


def test_hidden_tests_reference_expected_or_expect_error(
    exercises: list[SqlExercise],
) -> None:
    for e in exercises:
        for test in e.hidden_tests:
            assert test.expect_error or test.expected, (e.id, test.label)


def test_expect_error_tests_have_no_check_query(exercises: list[SqlExercise]) -> None:
    """expect_error checks the student's OWN query raising - a
    check_query on the same test would be dead/unused (see
    SqlHiddenTest and sql_execution_service._run_check).
    """
    for e in exercises:
        for test in e.hidden_tests:
            if test.expect_error:
                assert not test.check_query, (e.id, test.label)
