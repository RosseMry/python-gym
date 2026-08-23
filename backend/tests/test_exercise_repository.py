"""Tests for exercise retrieval and progress persistence."""

from __future__ import annotations

from app.domain.models import ExerciseStatus
from app.repositories.exercise_repository import ExerciseRepository


def test_get_existing_exercise_returns_it(repo: ExerciseRepository) -> None:
    exercise = repo.get("loop-003")
    assert exercise is not None
    assert exercise.title == "Sum the numbers"
    assert len(exercise.hidden_tests) == 2


def test_get_missing_exercise_returns_none(repo: ExerciseRepository) -> None:
    assert repo.get("does-not-exist") is None


def test_list_all_filters_by_module(repo: ExerciseRepository) -> None:
    assert [e.id for e in repo.list_all(module="for_loops")] == ["loop-003"]
    assert repo.list_all(module="lists") == []


def test_new_exercise_starts_with_new_progress(repo: ExerciseRepository) -> None:
    progress = repo.get_progress("loop-003")
    assert progress is not None
    assert progress.status == ExerciseStatus.NEW
    assert progress.attempts == 0
    assert progress.hints_used == 0


def test_save_progress_persists_changes(repo: ExerciseRepository) -> None:
    progress = repo.get_progress("loop-003")
    progress.attempts = 3
    progress.hints_used = 1
    progress.status = ExerciseStatus.SOLVED_WITH_HINT
    repo.save_progress(progress)

    reloaded = repo.get_progress("loop-003")
    assert reloaded.attempts == 3
    assert reloaded.hints_used == 1
    assert reloaded.status == ExerciseStatus.SOLVED_WITH_HINT


def test_solved_after_solution_status_round_trips(repo: ExerciseRepository) -> None:
    progress = repo.get_progress("loop-003")
    progress.status = ExerciseStatus.SOLVED_AFTER_SOLUTION
    repo.save_progress(progress)

    reloaded = repo.get_progress("loop-003")
    assert reloaded.status == ExerciseStatus.SOLVED_AFTER_SOLUTION
