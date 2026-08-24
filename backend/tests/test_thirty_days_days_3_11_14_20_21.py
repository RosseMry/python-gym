"""Regression tests for 30 Days of Python Days 3, 11, 14, 20, and 21
(Sprint 3 finalization, third correction, spec section 2). Day 3 had 2
real exercises with no day/level tag (invisible on the one-page view);
Days 11/14 had only Level 1 imported; Day 20 had only its first item;
Day 21 had only Level 1. Locks in that every produced exercise grades
correctly through the real sandbox, the same guarantee established for
the earlier Piscine and 30-Days corrections.
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

_TARGET_DAYS = {3, 11, 14, 20, 21}
# Exercises that are deliberately informational, not auto-graded - the
# same pattern as piscine-00-package (hidden_tests: [], script mode).
_NON_GRADABLE = {"30days-d20-03"}


def _load_all() -> list[Exercise]:
    paths = sorted((EXERCISES_DIR / "30_days_of_python").glob("30days-*.json"))
    exercises = [load_exercise(p) for p in paths]
    return [e for e in exercises if e.day in _TARGET_DAYS]


_EXERCISES = _load_all()
_IDS = [e.id for e in _EXERCISES]


def test_exactly_the_expected_days_are_covered() -> None:
    assert {e.day for e in _EXERCISES} == _TARGET_DAYS


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
        if len(line.strip()) > 12
        and not line.strip().startswith(("import ", "def ", "from ", "class "))
    }
    for hint in exercise.hints:
        assert hint.strip() != exercise.solution.strip()
        for line in solution_lines:
            assert line not in hint, (exercise.id, line, hint)


@pytest.mark.parametrize(
    "exercise",
    [e for e in _EXERCISES if e.resources],
    ids=[e.id for e in _EXERCISES if e.resources],
)
def test_file_dependent_exercise_resources_exist_on_disk(exercise: Exercise) -> None:
    resources_root = EXERCISES_DIR.parent / "resources"
    for resource in exercise.resources:
        assert (resources_root / resource).is_file(), (exercise.id, resource)
