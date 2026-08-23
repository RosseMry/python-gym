"""HTTP routes for the exercise engine."""

from __future__ import annotations

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


def get_service() -> ExerciseService:
    """Build a service instance with a fresh DB connection per request."""
    conn = get_connection()
    return ExerciseService(ExerciseRepository(conn))


class ExerciseSummary(BaseModel):
    id: str
    module: str
    difficulty: int
    title: str
    concepts: list[str]
    track: str
    source: str
    exercise_type: str


class ExerciseDetail(BaseModel):
    id: str
    module: str
    difficulty: int
    title: str
    description: str
    examples: str
    starter_code: str
    expected_behavior: str
    concepts: list[str]
    track: str
    source: str
    skills: list[str]
    prerequisites: list[str]
    resources: list[str]
    validation_profile: str
    exercise_type: str


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


class SolutionResponse(BaseModel):
    solution: str
    explanation: str


class ExplanationRequest(BaseModel):
    text: str


def _to_summary(exercise: Exercise) -> ExerciseSummary:
    return ExerciseSummary(
        id=exercise.id,
        module=exercise.module,
        difficulty=exercise.difficulty,
        title=exercise.title,
        concepts=exercise.concepts,
        track=exercise.track,
        source=exercise.source,
        exercise_type=exercise.exercise_type,
    )


def _to_detail(exercise: Exercise) -> ExerciseDetail:
    return ExerciseDetail(
        id=exercise.id,
        module=exercise.module,
        difficulty=exercise.difficulty,
        title=exercise.title,
        description=exercise.description,
        examples=exercise.examples,
        starter_code=exercise.starter_code,
        expected_behavior=exercise.expected_behavior,
        concepts=exercise.concepts,
        track=exercise.track,
        source=exercise.source,
        skills=exercise.skills,
        prerequisites=exercise.prerequisites,
        resources=exercise.resources,
        validation_profile=exercise.validation_profile,
        exercise_type=exercise.exercise_type,
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


@router.get("/{exercise_id}", response_model=ExerciseDetail)
def get_exercise(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> ExerciseDetail:
    """Return a single exercise, without its solution or hidden tests."""
    try:
        exercise = service.get_exercise_for_student(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    return _to_detail(exercise)


@router.post("/{exercise_id}/hint", response_model=HintResponse)
def request_hint(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> HintResponse:
    """Reveal the next unseen hint for this exercise."""
    try:
        hint = service.request_hint(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    return HintResponse(hint=hint)


@router.post("/{exercise_id}/solution", response_model=SolutionResponse)
def reveal_solution(
    exercise_id: str, service: ExerciseService = Depends(get_service)
) -> SolutionResponse:
    """Reveal the solution and explanation for this exercise."""
    try:
        solution, explanation = service.reveal_solution(exercise_id)
    except ExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exercise not found") from exc
    return SolutionResponse(solution=solution, explanation=explanation)


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
