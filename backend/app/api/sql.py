"""HTTP routes for the SQL exercise engine (Sprint 4)."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.sql_exercise_repository import SqlExerciseRepository
from app.services.sql_exercise_service import (
    SqlExerciseNotFoundError,
    SqlExerciseService,
)

router = APIRouter(prefix="/api/sql/exercises", tags=["sql"])


def get_service() -> Iterator[SqlExerciseService]:
    """Build a service instance with a fresh DB connection per request."""
    conn = get_connection()
    try:
        yield SqlExerciseService(SqlExerciseRepository(conn))
    finally:
        conn.close()


class SqlExerciseSummary(BaseModel):
    id: str
    module: str
    difficulty: int
    title: str
    source: str


class SqlExerciseDetail(BaseModel):
    id: str
    module: str
    difficulty: int
    title: str
    title_fr: str | None
    description: str
    description_fr: str | None
    starter_query: str
    expected_behavior: str
    concepts: list[str]
    skills: list[str]
    source: str
    postgres_note: str | None
    prerequisites: list[str]


class HintResponse(BaseModel):
    hint: str
    hint_fr: str | None


class SolutionResponse(BaseModel):
    solution: str
    explanation: str


class SubmissionRequest(BaseModel):
    query: str


class TestOutcomeResponse(BaseModel):
    label: str
    passed: bool
    detail: str


class SubmissionResponse(BaseModel):
    status: str
    passed: bool
    tests_total: int
    tests_passed: int
    tests: list[TestOutcomeResponse]
    result_columns: list[str]
    result_rows: list[list[str]]
    error: str | None
    execution_time: float


def _to_summary(exercise) -> SqlExerciseSummary:
    return SqlExerciseSummary(
        id=exercise.id,
        module=exercise.module,
        difficulty=exercise.difficulty,
        title=exercise.title,
        source=exercise.source,
    )


def _to_detail(exercise) -> SqlExerciseDetail:
    return SqlExerciseDetail(
        id=exercise.id,
        module=exercise.module,
        difficulty=exercise.difficulty,
        title=exercise.title,
        title_fr=exercise.title_fr,
        description=exercise.description,
        description_fr=exercise.description_fr,
        starter_query=exercise.starter_query,
        expected_behavior=exercise.expected_behavior,
        concepts=exercise.concepts,
        skills=exercise.skills,
        source=exercise.source,
        postgres_note=exercise.postgres_note,
        prerequisites=exercise.prerequisites,
    )


@router.get("", response_model=list[SqlExerciseSummary])
def list_sql_exercises(
    module: str | None = None,
    service: SqlExerciseService = Depends(get_service),
) -> list[SqlExerciseSummary]:
    """List all SQL exercises, optionally filtered by module (topic)."""
    return [_to_summary(e) for e in service.list_exercises(module)]


@router.get("/{exercise_id}", response_model=SqlExerciseDetail)
def get_sql_exercise(
    exercise_id: str, service: SqlExerciseService = Depends(get_service)
) -> SqlExerciseDetail:
    """Return a single SQL exercise, without its solution or hidden tests."""
    try:
        exercise = service.get_exercise_for_student(exercise_id)
    except SqlExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="SQL exercise not found") from exc
    return _to_detail(exercise)


@router.post("/{exercise_id}/hint", response_model=HintResponse)
def request_sql_hint(
    exercise_id: str, service: SqlExerciseService = Depends(get_service)
) -> HintResponse:
    """Reveal the next unseen hint for this SQL exercise."""
    try:
        hint, hint_fr = service.request_hint(exercise_id)
    except SqlExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="SQL exercise not found") from exc
    return HintResponse(hint=hint, hint_fr=hint_fr)


@router.post("/{exercise_id}/solution", response_model=SolutionResponse)
def reveal_sql_solution(
    exercise_id: str, service: SqlExerciseService = Depends(get_service)
) -> SolutionResponse:
    """Reveal the solution query and explanation for this exercise."""
    try:
        solution, explanation = service.reveal_solution(exercise_id)
    except SqlExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="SQL exercise not found") from exc
    return SolutionResponse(solution=solution, explanation=explanation)


@router.post("/{exercise_id}/submit", response_model=SubmissionResponse)
def submit_sql_solution(
    exercise_id: str,
    body: SubmissionRequest,
    service: SqlExerciseService = Depends(get_service),
) -> SubmissionResponse:
    """Run the student's query against the exercise's hidden tests."""
    try:
        result = service.submit(exercise_id, body.query)
    except SqlExerciseNotFoundError as exc:
        raise HTTPException(status_code=404, detail="SQL exercise not found") from exc
    return SubmissionResponse(
        status=result.status,
        passed=result.passed,
        tests_total=result.tests_total,
        tests_passed=result.tests_passed,
        tests=[
            TestOutcomeResponse(label=t.label, passed=t.passed, detail=t.detail)
            for t in result.tests
        ],
        result_columns=result.result_columns,
        result_rows=result.result_rows,
        error=result.error,
        execution_time=result.execution_time,
    )
