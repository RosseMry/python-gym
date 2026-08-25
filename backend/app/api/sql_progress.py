"""HTTP routes for SQL progress overview (Sprint 4, mirrors app.api.progress)."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.sql_exercise_repository import SqlExerciseRepository
from app.services.sql_exercise_service import SqlExerciseService

router = APIRouter(prefix="/api/sql/progress", tags=["sql"])


def get_service() -> Iterator[SqlExerciseService]:
    """Build a service instance with a fresh DB connection per request."""
    conn = get_connection()
    try:
        yield SqlExerciseService(SqlExerciseRepository(conn))
    finally:
        conn.close()


class SqlProgressItem(BaseModel):
    exercise_id: str
    status: str
    attempts: int
    hints_used: int
    solution_revealed: bool


@router.get("", response_model=list[SqlProgressItem])
def list_sql_progress(
    service: SqlExerciseService = Depends(get_service),
) -> list[SqlProgressItem]:
    """Return the raw progress record for every SQL exercise seen so far."""
    repo = service._repo  # simple MVP: read-only pass-through
    return [
        SqlProgressItem(
            exercise_id=p.exercise_id,
            status=p.status.value,
            attempts=p.attempts,
            hints_used=p.hints_used,
            solution_revealed=p.solution_revealed,
        )
        for p in repo.list_progress()
    ]
