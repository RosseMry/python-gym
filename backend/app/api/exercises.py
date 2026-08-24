"""HTTP routes for the exercise engine."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.domain.models import Exercise, SubmissionResult
from app.models.database import get_connection
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import (
    ExerciseNotFoundError,
    ExerciseService,
    InvalidRepeatRequestError,
)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


def get_service() -> Iterator[ExerciseService]:
    """Build a service instance with a fresh DB connection per request.

    A generator dependency so FastAPI closes the connection once the
    request finishes, regardless of which threadpool worker ran it -
    without this, connections opened here were never closed and
    accumulated across repeated requests (e.g. React StrictMode's
    double-fired dev effects), eventually causing 500s.
    """
    conn = get_connection()
    try:
        yield ExerciseService(ExerciseRepository(conn))
    finally:
        conn.close()


class ExerciseSummary(BaseModel):
    id: str
    module: str
    difficulty: int
    title: str
    title_fr: str | None
    concepts: list[str]
    track: str
    source: str
    exercise_type: str
    exercise_status: str
    day: int | None
    level: int | None


class PrerequisiteResponse(BaseModel):
    id: str
    title: str
    solved: bool


class ExerciseDetail(BaseModel):
    id: str
    module: str
    difficulty: int
    title: str
    title_fr: str | None
    description: str
    description_fr: str | None
    examples: str
    examples_fr: str | None
    starter_code: str
    expected_behavior: str
    expected_behavior_fr: str | None
    concepts: list[str]
    track: str
    source: str
    skills: list[str]
    prerequisites: list[PrerequisiteResponse]
    resources: list[str]
    validation_profile: str
    exercise_type: str
    exercise_status: str
    day: int | None
    level: int | None


class SubmissionRequest(BaseModel):
    code: str


class TestOutcomeResponse(BaseModel):
    label: str
    passed: bool
    detail: str


class StyleCheckResponse(BaseModel):
    ran: bool
    passed: bool
    output: str


class SubmissionResponse(BaseModel):
    status: str
    passed: bool
    tests_total: int
    tests_passed: int
    tests: list[TestOutcomeResponse]
    stdout: str
    stderr: str
    result: str | None
    execution_time: float
    error: str | None
    style: StyleCheckResponse | None


class HintResponse(BaseModel):
    hint: str
    hint_fr: str | None
    hint_function: str | None


class SolutionResponse(BaseModel):
    solution: str
    explanation: str
    explanation_fr: str | None


class ExplanationRequest(BaseModel):
    text: str


def _to_summary(exercise: Exercise) -> ExerciseSummary:
    return ExerciseSummary(
        id=exercise.id,
        module=exercise.module,
        difficulty=exercise.difficulty,
        title=exercise.title,
        title_fr=exercise.title_fr,
        concepts=exercise.concepts,
        track=exercise.track,
        source=exercise.source,
        exercise_type=exercise.exercise_type,
        exercise_status=exercise.exercise_status,
        day=exercise.day,
        level=exercise.level,
    )


def _to_detail(
    exercise: Exercise, prerequisites: list[dict] | None = None
) -> ExerciseDetail:
    return ExerciseDetail(
        id=exercise.id,
        module=exercise.module,
        difficulty=exercise.difficulty,
        title=exercise.title,
        title_fr=exercise.title_fr,
        description=exercise.description,
        description_fr=exercise.description_fr,
        examples=exercise.examples,
        examples_fr=exercise.examples_fr,
        starter_code=exercise.starter_code,
        expected_behavior=exercise.expected_behavior,
        expected_behavior_fr=exercise.expected_behavior_fr,
        concepts=exercise.concepts,
        track=exercise.track,
        source=exercise.source,
        skills=exercise.skills,
        prerequisites=[
            PrerequisiteResponse(**p) for p in (prerequisites or [])
        ],
        resources=exercise.resources,
        validation_profile=exercise.validation_profile,
        exercise_type=exercise.exercise_type,
        exercise_status=exercise.exercise_status,
        day=exercise.day,
        level=exercise.level,
    )


def _to_submission_response(result: SubmissionResult) -> SubmissionResponse:
    return SubmissionResponse(
        status=result.status,
        passed=result.passed,
        tests_total=result.tests_total,
        tests_passed=result.tests_passed,
        tests=[
            TestOutcomeResponse(label=t.label, passed=t.passed, detail=t.detail)
            for t in result.tests
        ],
        stdout=result.stdout,
        stderr=result.stderr,
        result=result.result,
        execution_time=result.execution_time,
        error=result.error,
        style=(
            StyleCheckResponse(
                ran=result.style.ran,
                passed=result.style.passed,
                output=result.style.output,
            )
            if result.style
            else None
        ),
    )


@router.get("", response_model=list[ExerciseSummary])
def list_exercises(
    module: str | None = None,
    source: str | None = None,
    service: ExerciseService = Depends(get_service),
) -> list[ExerciseSummary]:
    """List all exercises, optionally filtered by module or content source."""
    if source:
        exercises = service.list_by_source(source)
    else:
        exercises = service.list_exercises(module)
    return [_to_summary(e) for e in exercises]


@router.get("/repeat-queue", response_model=list[ExerciseSummary])
def get_repeat_queue(
    service: ExerciseService = Depends(get_service),
) -> list[ExerciseSummary]:
    """List exercises the student marked to repeat later (spec section 5)."""
    return [_to_summary(e) for e in service.list_repeat_queue()]


@router.get("/next", response_model=ExerciseSummary | None)
def get_next_exercise(
    source: str | None = None,
    service: ExerciseService = Depends(get_service),
) -> ExerciseSummary | None:
    """Recommend the next not-yet-solved exercise (basic learning path)."""
    exercise = service.get_next_unsolved(source)
    return _to_summary(exercise) if exercise else None


@router.get("/{exercise_id}", response_model=ExerciseDetail)
def get_exercise(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> ExerciseDetail:
    """Return a single exercise, without its solution or hidden tests."""
    try:
        exercise = service.get_exercise_for_student(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    prerequisites = service.resolve_prerequisites(exercise.prerequisites)
    return _to_detail(exercise, prerequisites)


@router.post("/{exercise_id}/hint", response_model=HintResponse)
def request_hint(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> HintResponse:
    """Reveal the next unseen hint for this exercise."""
    try:
        hint, hint_fr, hint_function = service.request_hint(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    return HintResponse(hint=hint, hint_fr=hint_fr, hint_function=hint_function)


@router.post("/{exercise_id}/solution", response_model=SolutionResponse)
def reveal_solution(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> SolutionResponse:
    """Reveal the solution and explanation for this exercise."""
    try:
        solution, explanation, explanation_fr = service.reveal_solution(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    return SolutionResponse(
        solution=solution, explanation=explanation, explanation_fr=explanation_fr
    )


@router.post("/{exercise_id}/submit", response_model=SubmissionResponse)
def submit_solution(
    exercise_id: str,
    body: SubmissionRequest,
    service: ExerciseService = Depends(get_service),
) -> SubmissionResponse:
    """Run the student's code against the exercise's hidden tests."""
    try:
        result = service.submit(exercise_id, body.code)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    return _to_submission_response(result)


@router.post("/{exercise_id}/repeat", status_code=204)
def mark_repeat(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> None:
    """Mark a solved exercise to be repeated later (spec sections 3-5)."""
    try:
        service.mark_repeat(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    except InvalidRepeatRequestError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{exercise_id}/explanation", status_code=204)
def submit_explanation(
    exercise_id: str,
    body: ExplanationRequest,
    service: ExerciseService = Depends(get_service),
) -> None:
    """Store the student's own explanation of why their code works."""
    try:
        service.save_explanation(exercise_id, body.text)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
