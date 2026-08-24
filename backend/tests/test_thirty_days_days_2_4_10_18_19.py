"""Regression tests for 30 Days of Python Days 2, 4, 10, 18, and 19
(Sprint 3 finalization, second correction, spec section 2). These were
entirely missing before this correction. Locks in that every produced
exercise actually grades correctly through the real sandbox - not just
that the JSON is well-formed - the same guarantee
test_piscine_module1_module2.py established for the 42 Piscine
Module 1/2 unlock.
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

_TARGET_DAYS = {2, 4, 10, 18, 19}


def _load_all() -> list[Exercise]:
    paths = sorted((EXERCISES_DIR / "30_days_of_python").glob("30days-d*.json"))
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
    # d02-l1-01 (file/comment setup) is the one deliberately non-gradable
    # entry, same pattern as piscine-00-package - every other exercise
    # must have at least one real hidden test.
    if exercise.id != "30days-d02-l1-01":
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
        and not line.strip().startswith(("import ", "def ", "from "))
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
