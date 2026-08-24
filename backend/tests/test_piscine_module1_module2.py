"""Regression tests for the 42 Piscine Module 1 (Array/NumPy) and
Module 2 (DataTable/pandas) exercises (Sprint 3 finalization, section
3): these were empty locked placeholders before this correction. Locks
in that they now ship real, gradable content - not just an unlocked
UI state - and that the hint progression stays learning-first rather
than leaking the solution (section 5, 8).
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

MODULE1_2_IDS = [
    "piscine-01-array2d",
    "piscine-01-give-bmi",
    "piscine-01-load-image",
    "piscine-01-rotate-image",
    "piscine-01-zoom-image",
    "piscine-01-pimp-image",
    "piscine-02-load-csv",
    "piscine-02-population-plot",
    "piscine-02-life-expectancy-plot",
    "piscine-02-income-projection",
]


def _load(exercise_id: str) -> Exercise:
    path = EXERCISES_DIR / "42_python_piscine" / f"{exercise_id}.json"
    return load_exercise(path)


@pytest.mark.parametrize("exercise_id", MODULE1_2_IDS)
def test_exercise_is_active_with_real_content(exercise_id: str) -> None:
    exercise = _load(exercise_id)
    assert exercise.exercise_status == "active"
    assert exercise.starter_code.strip()
    assert exercise.hidden_tests
    assert exercise.solution.strip()


@pytest.mark.parametrize("exercise_id", MODULE1_2_IDS)
def test_reference_solution_passes_every_hidden_test(exercise_id: str) -> None:
    exercise = _load(exercise_id)
    result = run_submission(exercise, exercise.solution)
    assert result.passed, (exercise_id, result.error, result.tests)
    assert result.tests_passed == result.tests_total


@pytest.mark.parametrize("exercise_id", MODULE1_2_IDS)
def test_unmodified_starter_code_does_not_pass(exercise_id: str) -> None:
    """Guards against an accidentally-too-easy hidden test."""
    exercise = _load(exercise_id)
    result = run_submission(exercise, exercise.starter_code)
    assert not result.passed


@pytest.mark.parametrize("exercise_id", MODULE1_2_IDS)
def test_hints_teach_before_revealing_and_never_leak_the_solution(
    exercise_id: str,
) -> None:
    """No hint may contain a full line of the solution's actual code -
    prose that mentions what a method *does* (e.g. "returns the n
    largest rows") is fine and expected; a copy-pasted code line is not.
    """
    exercise = _load(exercise_id)
    assert len(exercise.hints) == 3
    solution_lines = {
        line.strip()
        for line in exercise.solution.splitlines()
        if line.strip() and not line.strip().startswith(("import ", "def "))
    }
    for hint in exercise.hints:
        assert hint.strip() != exercise.solution.strip()
        for line in solution_lines:
            assert line not in hint, (exercise_id, line, hint)


_NO_RESOURCE_NEEDED = {"piscine-01-array2d", "piscine-01-give-bmi"}


@pytest.mark.parametrize(
    "exercise_id",
    [i for i in MODULE1_2_IDS if i not in _NO_RESOURCE_NEEDED],
)
def test_file_dependent_exercise_declares_its_resource(exercise_id: str) -> None:
    """Every image/CSV exercise must list the resource file the
    execution sandbox needs to stage, or the submission can't run.
    """
    exercise = _load(exercise_id)
    assert exercise.resources
