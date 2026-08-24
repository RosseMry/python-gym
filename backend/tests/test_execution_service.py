"""Tests for the isolated subprocess execution of student code."""

from __future__ import annotations

from app.domain.models import Exercise, HiddenTest
from app.services.execution_service import run_submission

EXERCISE = Exercise(
    id="x",
    module="for_loops",
    difficulty=1,
    title="x",
    description="x",
    examples="x",
    starter_code="x",
    hints=[],
    expected_behavior="x",
    hidden_tests=[
        HiddenTest(call="add(2, 3)", expected="5"),
        HiddenTest(call="add(-1, 1)", expected="0"),
    ],
    solution="def add(a, b):\n    return a + b\n",
    explanation="x",
    concepts=[],
)


def test_correct_code_passes_all_tests() -> None:
    result = run_submission(EXERCISE, "def add(a, b):\n    return a + b\n")
    assert result.passed is True
    assert result.tests_passed == 2
    assert result.tests_total == 2


def test_partial_correct_code_reports_partial_pass() -> None:
    result = run_submission(EXERCISE, "def add(a, b):\n    return 5\n")
    assert result.passed is False
    assert result.tests_passed == 1  # only add(2, 3) == 5 happens to match


def test_syntax_error_does_not_crash_the_service() -> None:
    result = run_submission(EXERCISE, "def add(a, b)\n    return a + b\n")
    assert result.passed is False
    assert result.tests_passed == 0


NO_HIDDEN_TESTS_EXERCISE = Exercise(
    id="x-no-tests",
    module="for_loops",
    difficulty=1,
    title="x",
    description="x",
    examples="x",
    starter_code="def add(a, b):\n    pass\n",
    hints=[],
    expected_behavior="x",
    hidden_tests=[],
    solution="def add(a, b):\n    return a + b\n",
    explanation="x",
    concepts=[],
)


def test_function_mode_with_no_hidden_tests_reports_passed() -> None:
    """Regression test: exercises with output that can't be asserted
    exactly (e.g. piscine-00-loading's live progress bar, or a
    packaging exercise with nothing to call) ship with hidden_tests=[]
    and are meant to be manually verified - before this fix, function
    mode always reported them as failed regardless of the submission,
    unlike script mode's equivalent tests_total == 0 case.
    """
    result = run_submission(NO_HIDDEN_TESTS_EXERCISE, NO_HIDDEN_TESTS_EXERCISE.solution)
    assert result.passed is True
    assert result.status == "passed"
    assert result.tests_total == 0


def test_missing_function_fails_gracefully() -> None:
    result = run_submission(EXERCISE, "x = 1\n")
    assert result.passed is False
    assert result.tests_passed == 0


def test_infinite_loop_times_out_instead_of_hanging() -> None:
    result = run_submission(EXERCISE, "def add(a, b):\n    while True:\n        pass\n")
    assert result.passed is False
    assert result.error is not None
    assert "timed out" in result.error
