"""Tests for marking exercises to repeat later (Sprint 2 spec sections 3-5)."""

from __future__ import annotations

import pytest

from app.domain.models import ExerciseStatus
from app.services.exercise_service import (
    ExerciseService,
    InvalidRepeatRequestError,
)

CORRECT = (
    "def sum_numbers(numbers):\n"
    "    total = 0\n"
    "    for number in numbers:\n"
    "        total += number\n"
    "    return total\n"
)


def test_cannot_mark_repeat_before_solving(service: ExerciseService) -> None:
    with pytest.raises(InvalidRepeatRequestError):
        service.mark_repeat("loop-003")


def test_cannot_mark_repeat_after_a_failed_attempt(service: ExerciseService) -> None:
    service.submit("loop-003", "def sum_numbers(numbers):\n    return -1\n")
    with pytest.raises(InvalidRepeatRequestError):
        service.mark_repeat("loop-003")


def test_mark_repeat_after_solving(service: ExerciseService) -> None:
    service.submit("loop-003", CORRECT)
    service.mark_repeat("loop-003")

    progress = service._repo.get_progress("loop-003")
    assert progress.status == ExerciseStatus.SOLVED_TO_REPEAT


def test_repeat_is_not_mastery(service: ExerciseService) -> None:
    """Repeat must never be conflated with mastery (spec section 9)."""
    service.submit("loop-003", CORRECT)
    service.mark_repeat("loop-003")
    service.submit("loop-003", CORRECT)  # solved again, cleanly

    progress = service._repo.get_progress("loop-003")
    # A second clean solve after a plain SOLVED->repeat cycle should not
    # jump straight to MASTERED - it takes another clean solve from here.
    assert progress.status == ExerciseStatus.SOLVED


def test_repeat_queue_lists_marked_exercises(service: ExerciseService) -> None:
    assert service.list_repeat_queue() == []
    service.submit("loop-003", CORRECT)
    service.mark_repeat("loop-003")

    queue = service.list_repeat_queue()
    assert [e.id for e in queue] == ["loop-003"]


def test_solving_again_removes_exercise_from_repeat_queue(
    service: ExerciseService,
) -> None:
    service.submit("loop-003", CORRECT)
    service.mark_repeat("loop-003")
    assert len(service.list_repeat_queue()) == 1

    service.submit("loop-003", CORRECT)
    assert service.list_repeat_queue() == []


def test_mark_repeat_on_missing_exercise_raises(service: ExerciseService) -> None:
    from app.services.exercise_service import ExerciseNotFoundError

    with pytest.raises(ExerciseNotFoundError):
        service.mark_repeat("does-not-exist")
