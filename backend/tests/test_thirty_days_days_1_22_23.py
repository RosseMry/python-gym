"""Regression tests for 30 Days of Python Days 1, 22, and 23 (Sprint 3
finalization, fifth correction). Day 1 has no exercise list at all in
the source - it's built from the real Day 1 walkthrough script
instead. Day 22 (web scraping) and Day 23 (virtual environment) were
locked in ThirtyDaysPage.tsx as needing live network / not being
gradable - checked directly rather than assumed: two of Day 22's three
scraping targets have been redesigned since the source repo was
written (no longer have a scrapable table) and one target (Wikipedia's
presidents table) still works, bundled as a real static snapshot. Day
23's single source item is pure CLI/tooling with no code to check, so
one reference entry plus one thematically-related, clearly-disclosed
bonus exercise represent it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import Exercise  # noqa: E402
from app.services.execution_service import run_submission  # noqa: E402
from scripts.seed import EXERCISES_DIR, load_exercise  # noqa: E402

_TARGET_DAYS = {1, 22, 23}
_NON_GRADABLE = {"30days-d22-02", "30days-d23-01"}


def _load_all() -> list[Exercise]:
    paths = sorted((EXERCISES_DIR / "30_days_of_python").glob("30days-d*.json"))
    exercises = [load_exercise(p) for p in paths]
    return [e for e in exercises if e.day in _TARGET_DAYS]


_EXERCISES = _load_all()
_IDS = [e.id for e in _EXERCISES]


def test_exactly_the_expected_days_are_covered() -> None:
    assert {e.day for e in _EXERCISES} == _TARGET_DAYS


def test_each_day_has_exactly_two_exercises() -> None:
    by_day: dict[int, int] = {}
    for exercise in _EXERCISES:
        by_day[exercise.day] = by_day.get(exercise.day, 0) + 1
    assert by_day == {1: 2, 22: 2, 23: 2}


@pytest.mark.parametrize("exercise", _EXERCISES, ids=_IDS)
def test_exercise_is_active_with_real_content(exercise: Exercise) -> None:
    assert exercise.exercise_status == "active"
    assert exercise.starter_code.strip()
    assert exercise.solution.strip()
    if exercise.id not in _NON_GRADABLE:
        assert exercise.hidden_tests, exercise.id


@pytest.mark.parametrize("exercise", _EXERCISES, ids=_IDS)
def test_reference_solution_passes_every_hidden_test(exercise: Exercise) -> None:
    result = run_submission(exercise, exercise.solution)
    assert result.passed, (exercise.id, result.error, result.tests)
    assert result.tests_passed == result.tests_total


@pytest.mark.parametrize(
    "exercise",
    [e for e in _EXERCISES if e.hidden_tests],
    ids=[e.id for e in _EXERCISES if e.hidden_tests],
)
def test_unmodified_starter_code_does_not_pass(exercise: Exercise) -> None:
    result = run_submission(exercise, exercise.starter_code)
    assert not result.passed, exercise.id


@pytest.mark.parametrize("exercise", _EXERCISES, ids=_IDS)
def test_hints_teach_before_revealing_and_never_leak_the_solution(
    exercise: Exercise,
) -> None:
    assert len(exercise.hints) == 3, exercise.id
    solution_lines = {
        line.strip()
        for line in exercise.solution.splitlines()
        if len(line.strip()) > 20
        and not line.strip().startswith(("import ", "def ", "from ", "class "))
    }
    for hint in exercise.hints:
        assert hint.strip() != exercise.solution.strip()
        for line in solution_lines:
            assert line not in hint, (exercise.id, line, hint)


def test_presidents_table_resource_exists_on_disk() -> None:
    resource = (
        EXERCISES_DIR.parent
        / "resources"
        / "python"
        / "30-days"
        / "us_presidents_table.html"
    )
    assert resource.is_file()
