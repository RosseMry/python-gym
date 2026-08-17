"""HTTP routes for progress overview (basic version for Sprint 1).

Sprint 2 will extend this with per-module fluency percentages,
streaks and weakest concepts (spec section 24).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/api/progress", tags=["progress"])


def get_service() -> ExerciseService:
    conn = get_connection()
    return ExerciseService(ExerciseRepository(conn))


class ProgressItem(BaseModel):
    exercise_id: str
    status: str
    attempts: int
    hints_used: int
    solution_revealed: bool


@router.get("", response_model=list[ProgressItem])
def list_progress(service: ExerciseService = Depends(get_service)) -> list[ProgressItem]:
    """Return the raw progress record for every exercise seen so far."""
    repo = service._repo  # simple MVP: read-only pass-through
    return [
        ProgressItem(
            exercise_id=p.exercise_id,
            status=p.status.value,
            attempts=p.attempts,
            hints_used=p.hints_used,
            solution_revealed=p.solution_revealed,
        )
        for p in repo.list_progress()
    ]
