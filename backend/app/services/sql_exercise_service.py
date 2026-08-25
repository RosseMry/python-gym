"""Business logic for SQL exercises: hints, submissions, progress.

Mirrors ExerciseService's rules (never leak the solution early, hint-
using or solution-revealed passes don't count as mastery) applied to
SqlExercise/SqlHiddenTest instead of Exercise/HiddenTest - the mastery
state machine itself (ExerciseStatus) is shared, not duplicated.
"""

from __future__ import annotations

from app.domain.models import (
    ExerciseStatus,
    ProgressEntry,
    SqlExercise,
    SqlSubmissionResult,
)
from app.repositories.sql_exercise_repository import SqlExerciseRepository
from app.services.sql_execution_service import run_sql_submission

_SOLVED_FAMILY = (
    ExerciseStatus.SOLVED,
    ExerciseStatus.SOLVED_WITH_HINT,
    ExerciseStatus.SOLVED_AFTER_SOLUTION,
    ExerciseStatus.SOLVED_TO_REPEAT,
    ExerciseStatus.MASTERED,
)


class SqlExerciseNotFoundError(Exception):
    """Raised when a SQL exercise id does not exist."""


class SqlExerciseService:
    """Coordinates the SQL repository + grading engine for the SQL track."""

    def __init__(self, repository: SqlExerciseRepository) -> None:
        self._repo = repository

    def list_exercises(self, module: str | None = None) -> list[SqlExercise]:
        return self._repo.list_all(module)

    def get_exercise_for_student(self, exercise_id: str) -> SqlExercise:
        """Return an exercise with the answer stripped out.

        Solution and hidden tests are never sent to the frontend
        directly - only used server-side for grading, or exposed
        explicitly via ``reveal_solution``.
        """
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise SqlExerciseNotFoundError(exercise_id)
        return SqlExercise(
            id=exercise.id,
            module=exercise.module,
            difficulty=exercise.difficulty,
            title=exercise.title,
            description=exercise.description,
            starter_query=exercise.starter_query,
            hints=[],
            expected_behavior=exercise.expected_behavior,
            hidden_tests=[],
            solution="",
            explanation="",
            concepts=exercise.concepts,
            skills=exercise.skills,
            source=exercise.source,
            postgres_note=exercise.postgres_note,
            prerequisites=exercise.prerequisites,
            exercise_status=exercise.exercise_status,
            title_fr=exercise.title_fr,
            description_fr=exercise.description_fr,
        )

    def request_hint(self, exercise_id: str) -> tuple[str, str | None]:
        """Reveal the next hint the student hasn't seen yet."""
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise SqlExerciseNotFoundError(exercise_id)
        progress = self._repo.get_progress(exercise_id)

        if progress.hints_used >= len(exercise.hints):
            return "No more hints available for this exercise.", None

        index = progress.hints_used
        hint_text = exercise.hints[index]
        hint_text_fr = (
            exercise.hints_fr[index]
            if exercise.hints_fr and index < len(exercise.hints_fr)
            else None
        )
        progress.hints_used += 1
        if progress.status == ExerciseStatus.NEW:
            progress.status = ExerciseStatus.ATTEMPTED
        self._repo.save_progress(progress)
        return hint_text, hint_text_fr

    def reveal_solution(self, exercise_id: str) -> tuple[str, str]:
        """Explicitly reveal the solution query and explanation."""
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise SqlExerciseNotFoundError(exercise_id)
        progress = self._repo.get_progress(exercise_id)
        progress.solution_revealed = True
        self._repo.save_progress(progress)
        return exercise.solution, exercise.explanation

    def submit(self, exercise_id: str, query: str) -> SqlSubmissionResult:
        """Run the student's query and update progress/mastery status."""
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise SqlExerciseNotFoundError(exercise_id)

        result = run_sql_submission(exercise, query)

        progress = self._repo.get_progress(exercise_id)
        progress.attempts += 1

        self._repo.record_submission(
            exercise_id=exercise_id,
            query=query,
            passed=result.passed,
            tests_total=result.tests_total,
            tests_passed=result.tests_passed,
            status=result.status,
        )

        if result.passed:
            progress.status = self._next_status_on_success(progress)
        else:
            progress.status = ExerciseStatus.FAILED

        self._repo.save_progress(progress)
        return result

    def mark_repeat(self, exercise_id: str) -> None:
        if self._repo.get(exercise_id) is None:
            raise SqlExerciseNotFoundError(exercise_id)
        progress = self._repo.get_progress(exercise_id)
        if progress.status not in _SOLVED_FAMILY:
            raise ValueError("Only a solved exercise can be marked to repeat later.")
        progress.status = ExerciseStatus.SOLVED_TO_REPEAT
        self._repo.save_progress(progress)

    def _next_status_on_success(self, progress: ProgressEntry) -> ExerciseStatus:
        """Same mastery rule as the Python track (spec section 13/21):
        a pass right after revealing the solution, or after using a
        hint, does not count as full mastery.
        """
        if progress.solution_revealed:
            return ExerciseStatus.SOLVED_AFTER_SOLUTION
        if progress.hints_used > 0:
            return ExerciseStatus.SOLVED_WITH_HINT
        if progress.status in (ExerciseStatus.SOLVED, ExerciseStatus.MASTERED):
            return ExerciseStatus.MASTERED
        return ExerciseStatus.SOLVED
