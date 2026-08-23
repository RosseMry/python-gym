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
    StyleCheckResult,
    SubmissionResult,
)
from app.repositories.exercise_repository import ExerciseRepository
from app.services.execution_service import run_submission
from app.services.style_service import check_style

# Solved-with-hint exercises need this many additional clean solves
# before they count as MASTERED (kept simple for the MVP).
_MASTERY_STREAK_REQUIRED = 2

# Progress states that mean "this was solved at some point" - used to
# decide whether marking an exercise for repeat makes sense (spec
# section 5) and whether a fresh clean solve should count toward
# mastery (spec section 21).
_SOLVED_FAMILY = (
    ExerciseStatus.SOLVED,
    ExerciseStatus.SOLVED_WITH_HINT,
    ExerciseStatus.SOLVED_AFTER_SOLUTION,
    ExerciseStatus.SOLVED_TO_REPEAT,
    ExerciseStatus.MASTERED,
)


class ExerciseNotFoundError(Exception):
    """Raised when an exercise id does not exist."""


class InvalidRepeatRequestError(Exception):
    """Raised when repeat is requested for an exercise that isn't solved."""


class ExerciseService:
    """Coordinates repository + execution to implement the learning flow."""

    def __init__(self, repository: ExerciseRepository) -> None:
        self._repo = repository

    def list_exercises(self, module: str | None = None) -> list[Exercise]:
        """List exercises, optionally filtered by module."""
        return self._repo.list_all(module)

    def list_by_source(self, source: str) -> list[Exercise]:
        """List exercises for a single content source (spec section 18)."""
        return self._repo.list_by_source(source)

    def list_repeat_queue(self) -> list[Exercise]:
        """List exercises the student marked to repeat later (section 5)."""
        return self._repo.list_repeat_queue()

    def resolve_prerequisites(self, exercise_ids: list[str]) -> list[dict]:
        """Resolve prerequisite ids into displayable, solved-aware links."""
        return self._repo.resolve_prerequisites(exercise_ids)

    def get_next_unsolved(self, source: str | None = None) -> Exercise | None:
        """Recommend the next not-yet-solved exercise (basic learning path)."""
        return self._repo.get_next_unsolved(source)

    def get_exercise_for_student(self, exercise_id: str) -> Exercise:
        """Return an exercise with the answer stripped out.

        Solution and hidden tests are never sent to the frontend
        directly - they are only used server-side for grading, or
        exposed explicitly via ``reveal_solution``. Sprint 2 metadata
        (track, source, skills, prerequisites, validation profile) is
        not sensitive and is passed through for the sidebar/learning
        path to use.
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
            track=exercise.track,
            source=exercise.source,
            skills=exercise.skills,
            prerequisites=exercise.prerequisites,
            resources=exercise.resources,
            validation_profile=exercise.validation_profile,
            exercise_type=exercise.exercise_type,
            exercise_status=exercise.exercise_status,
            day=exercise.day,
            level=exercise.level,
            title_fr=exercise.title_fr,
            description_fr=exercise.description_fr,
            examples_fr=exercise.examples_fr,
            expected_behavior_fr=exercise.expected_behavior_fr,
            # explanation_fr/hints_fr stay off the student-facing copy,
            # same as explanation/hints - they're only revealed via
            # request_hint()/reveal_solution().
        )

    def request_hint(self, exercise_id: str) -> tuple[str, str | None]:
        """Reveal the next hint the student hasn't seen yet.

        Returns ``(hint, hint_fr)`` - ``hint_fr`` is ``None`` when that
        hint hasn't been translated yet, so the frontend falls back to
        the English text.
        """
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(exercise_id)
        progress = self._get_or_create_progress(exercise_id)

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

    def reveal_solution(self, exercise_id: str) -> tuple[str, str, str | None]:
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
        return exercise.solution, exercise.explanation, exercise.explanation_fr

    def submit(self, exercise_id: str, code: str) -> SubmissionResult:
        """Run the student's code and update progress/mastery status.

        Sprint 2 (spec section 32) runs a style check alongside the
        hidden tests, but only for exercises whose validation profile
        asks for it - style is never a hidden-test failure, it's
        surfaced as a separate ``style`` field on the result.
        """
        exercise = self._repo.get(exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(exercise_id)

        result = run_submission(exercise, code)
        if exercise.validation_profile == "42_piscine":
            result = _with_style_check(result, code)

        progress = self._get_or_create_progress(exercise_id)
        progress.attempts += 1

        submission_status = "passed" if result.passed else result.status
        self._repo.record_submission(
            exercise_id=exercise_id,
            code=code,
            passed=result.passed,
            tests_total=result.tests_total,
            tests_passed=result.tests_passed,
            status=submission_status,
            hints_used_snapshot=progress.hints_used,
            solution_revealed_snapshot=progress.solution_revealed,
        )

        if result.passed:
            progress.status = self._next_status_on_success(progress)
        else:
            progress.status = ExerciseStatus.FAILED

        self._repo.save_progress(progress)
        return result

    def mark_repeat(self, exercise_id: str) -> None:
        """Mark a solved exercise as needing to be repeated later.

        Sprint 2 spec sections 3-5: this is only meaningful for an
        exercise the student has actually solved. It does not count as
        mastery, and is distinct from FAILED.
        """
        if self._repo.get(exercise_id) is None:
            raise ExerciseNotFoundError(exercise_id)
        progress = self._get_or_create_progress(exercise_id)
        if progress.status not in _SOLVED_FAMILY:
            raise InvalidRepeatRequestError(
                "Only a solved exercise can be marked to repeat later."
            )
        progress.status = ExerciseStatus.SOLVED_TO_REPEAT
        self._repo.save_progress(progress)

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
        Revealing the solution and using a hint are tracked as distinct
        statuses (Sprint 3 correction) since they're different signals
        for the future adaptive/exam system, even though neither counts
        toward mastery on this pass.
        """
        if progress.solution_revealed:
            return ExerciseStatus.SOLVED_AFTER_SOLUTION
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


def _with_style_check(result: SubmissionResult, code: str) -> SubmissionResult:
    """Attach a style-check result without touching test pass/fail.

    Spec section 32 - style is reported separately and never silently
    folded into the hidden-test result.
    """
    ran, passed, output = check_style(code)
    return SubmissionResult(
        status=result.status,
        passed=result.passed,
        tests_total=result.tests_total,
        tests_passed=result.tests_passed,
        tests=result.tests,
        stdout=result.stdout,
        stderr=result.stderr,
        result=result.result,
        execution_time=result.execution_time,
        error=result.error,
        style=StyleCheckResult(ran=ran, passed=passed, output=output),
    )
