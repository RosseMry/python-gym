"""Tests for the exercise service: hints, submission grading, mastery."""

from __future__ import annotations

import pytest

from app.domain.models import ExerciseStatus
from app.services.exercise_service import ExerciseNotFoundError, ExerciseService

CORRECT = (
    "def sum_numbers(numbers):\n"
    "    total = 0\n"
    "    for number in numbers:\n"
    "        total += number\n"
    "    return total\n"
)

WRONG = "def sum_numbers(numbers):\n    return 0\n"

BROKEN = "def sum_numbers(numbers):\n    return numbers +\n"  # syntax error


def test_get_exercise_hides_solution_and_hidden_tests(
    service: ExerciseService,
) -> None:
    exercise = service.get_exercise_for_student("loop-003")
    assert exercise.solution == ""
    assert exercise.hidden_tests == []
    assert exercise.hints == []


def test_get_missing_exercise_raises(service: ExerciseService) -> None:
    with pytest.raises(ExerciseNotFoundError):
        service.get_exercise_for_student("nope")


def test_hints_are_revealed_one_at_a_time(service: ExerciseService) -> None:
    assert service.request_hint("loop-003") == "hint 1"
    assert service.request_hint("loop-003") == "hint 2"
    assert "total = 0" in service.request_hint("loop-003")
    assert (
        service.request_hint("loop-003")
        == "No more hints available for this exercise."
    )


def test_correct_submission_passes_and_marks_solved(
    service: ExerciseService,
) -> None:
    result = service.submit("loop-003", CORRECT)
    assert result.passed is True
    assert result.tests_passed == result.tests_total == 2

    progress = service._repo.get_progress("loop-003")
    assert progress.status == ExerciseStatus.SOLVED
    assert progress.attempts == 1


def test_wrong_submission_fails_and_marks_failed(
    service: ExerciseService,
) -> None:
    result = service.submit("loop-003", WRONG)
    assert result.passed is False
    # WRONG always returns 0, which happens to match the empty-list case,
    # so it should pass exactly 1 of the 2 hidden tests, not all of them.
    assert result.tests_passed == 1
    assert result.tests_total == 2

    progress = service._repo.get_progress("loop-003")
    # Sprint 2: a failed submission is its own state, distinct from the
    # "requested a hint but hasn't submitted" ATTEMPTED state.
    assert progress.status == ExerciseStatus.FAILED
    assert progress.attempts == 1


def test_broken_code_fails_gracefully(service: ExerciseService) -> None:
    result = service.submit("loop-003", BROKEN)
    assert result.passed is False
    assert result.tests_passed == 0


def test_solving_after_using_a_hint_does_not_count_as_full_mastery(
    service: ExerciseService,
) -> None:
    service.request_hint("loop-003")
    result = service.submit("loop-003", CORRECT)

    assert result.passed is True
    progress = service._repo.get_progress("loop-003")
    assert progress.status == ExerciseStatus.SOLVED_WITH_HINT


def test_two_clean_solves_lead_to_mastery(service: ExerciseService) -> None:
    service.submit("loop-003", CORRECT)
    result = service.submit("loop-003", CORRECT)

    assert result.passed is True
    progress = service._repo.get_progress("loop-003")
    assert progress.status == ExerciseStatus.MASTERED


def test_revealing_solution_prevents_full_mastery_on_next_pass(
    service: ExerciseService,
) -> None:
    solution, explanation = service.reveal_solution("loop-003")
    assert "total" in solution
    assert explanation == "Accumulator pattern."

    result = service.submit("loop-003", CORRECT)
    assert result.passed is True
    progress = service._repo.get_progress("loop-003")
    assert progress.status == ExerciseStatus.SOLVED_WITH_HINT


def test_explanation_is_stored(service: ExerciseService) -> None:
    service.save_explanation("loop-003", "I use total to accumulate values.")
    row = service._repo._conn.execute(
        "SELECT text FROM explanations WHERE exercise_id = ?", ("loop-003",)
    ).fetchone()
    assert row["text"] == "I use total to accumulate values."


def test_explanation_on_missing_exercise_raises(service: ExerciseService) -> None:
    with pytest.raises(ExerciseNotFoundError):
        service.save_explanation("nope", "text")
