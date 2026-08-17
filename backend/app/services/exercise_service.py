"""Business logic for exercises: hints, submissions, progress, mastery.

This is where the "never show the solution too early" rule (spec
section 3) is enforced. The repository only stores data; this service
decides what is allowed to happen and when.
"""

from __future__ import annotations

from app.domain.models import (
    Exercise,
    ExerciseStatus,
    ProgressEntry,
    SubmissionResult,
)
from app.repositories.exercise_repository import ExerciseRepository
from app.services.execution_service import run_submission

# Solved-with-hint exercises need this many additional clean solves
# before they count as MASTERED (kept simple for the MVP).
_MASTERY_STREAK_REQUIRED = 2


class ExerciseNotFoundError(Exception):
    """Raised when an exercise id does not exist."""


class ExerciseService:
    """Coordinates repository + execution to implement the learning flow."""

    def __init__(self, repository: ExerciseRepository) -> None:
        self._repo = repository

    def list_exercises(self, module: str | None = None) -> list[Exercise]:
        """List exercises, optionally filtered by module."""
        return self._repo.list_all(module)

    def get_exercise_for_student(self, exercise_id: str) -> Exercise:
        """Return an exercise with the answer stripped out.

        Solution and hidden tests are never sent to the frontend
        directly - they are only used server-side for grading, or
        exposed explicitly via ``reveal_solution``.
        """
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(exercise_id)
        return Exercise(
            id=exercise.id,
            module=exercise.module,
            difficulty=exercise.difficulty,
            title=exercise.title,
            description=exercise.description,
            examples=exercise.examples,
            starter_code=exercise.starter_code,
            hints=[],  # hints are requested one at a time, see request_hint
            expected_behavior=exercise.expected_behavior,
            hidden_tests=[],
            solution="",
            explanation="",
            concepts=exercise.concepts,
        )

    def request_hint(self, exercise_id: str) -> str:
        """Reveal the next hint the student hasn't seen yet."""
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(exercise_id)
        progress = self._get_or_create_progress(exercise_id)

        if progress.hints_used >= len(exercise.hints):
            return "No more hints available for this exercise."

        hint_text = exercise.hints[progress.hints_used]
        progress.hints_used += 1
        if progress.status == ExerciseStatus.NEW:
            progress.status = ExerciseStatus.ATTEMPTED
        self._repo.save_progress(progress)
        return hint_text

    def reveal_solution(self, exercise_id: str) -> tuple[str, str]:
        """Explicitly reveal the solution and explanation.

        This should only be called by the frontend after the student
        has gone through attempts and hints (spec section 20/26) - the
        API does not block it outright so an instructor/self-review
        flow stays possible, but the frontend UI should gate it.
        """
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(exercise_id)
        progress = self._get_or_create_progress(exercise_id)
        progress.solution_revealed = True
        self._repo.save_progress(progress)
        return exercise.solution, exercise.explanation

    def submit(self, exercise_id: str, code: str) -> SubmissionResult:
        """Run the student's code and update progress/mastery status."""
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(exercise_id)

        result = run_submission(exercise, code)

        progress = self._get_or_create_progress(exercise_id)
        progress.attempts += 1
        self._repo.record_submission(
            exercise_id=exercise_id,
            code=code,
            passed=result.passed,
            tests_total=result.tests_total,
            tests_passed=result.tests_passed,
        )

        if result.passed:
            progress.status = self._next_status_on_success(progress)
        elif progress.status == ExerciseStatus.NEW:
            progress.status = ExerciseStatus.ATTEMPTED

        self._repo.save_progress(progress)
        return result

    def save_explanation(self, exercise_id: str, text: str) -> None:
        """Store the student's free-text explanation of their solution."""
        if self._repo.get(exercise_id) is None:
            raise ExerciseNotFoundError(exercise_id)
        self._repo.save_explanation(exercise_id, text)

    def _next_status_on_success(self, progress: ProgressEntry) -> ExerciseStatus:
        """Decide the new status after a passing submission.

        A pass right after the solution was revealed, or after using
        hints, does NOT count as full mastery (spec section 21) - it
        must be solved cleanly, more than once, to become MASTERED.
        """
        if progress.solution_revealed:
            return ExerciseStatus.SOLVED_WITH_HINT
        if progress.hints_used > 0:
            return ExerciseStatus.SOLVED_WITH_HINT
        if progress.status in (
            ExerciseStatus.SOLVED,
            ExerciseStatus.MASTERED,
        ):
            return ExerciseStatus.MASTERED
        return ExerciseStatus.SOLVED

    def _get_or_create_progress(self, exercise_id: str) -> ProgressEntry:
        progress = self._repo.get_progress(exercise_id)
        if progress is None:
            progress = ProgressEntry(
                exercise_id=exercise_id,
                status=ExerciseStatus.NEW,
                attempts=0,
                hints_used=0,
                solution_revealed=False,
            )
        return progress
