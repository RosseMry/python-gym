"""HTTP routes for the Function Reference catalog (Sprint 3 finalization).

Reusable explanations a hint can point to (e.g. "sum()") instead of
duplicating the same explanation in every exercise that happens to use
that function.
"""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.function_reference_repository import (
    FunctionReferenceRepository,
)

router = APIRouter(prefix="/api/functions", tags=["functions"])


def get_repository() -> Iterator[FunctionReferenceRepository]:
    """Build a repository with a fresh, request-scoped DB connection."""
    conn = get_connection()
    try:
        yield FunctionReferenceRepository(conn)
    finally:
        conn.close()


class FunctionReferenceSummary(BaseModel):
    id: str
    name: str
    name_fr: str | None


class FunctionReferenceDetail(BaseModel):
    id: str
    name: str
    name_fr: str | None
    what_it_does: str
    what_it_does_fr: str | None
    syntax: str
    parameters: str
    parameters_fr: str | None
    return_value: str
    return_value_fr: str | None
    example: str
    example_output: str
    common_mistakes: str
    common_mistakes_fr: str | None
    when_to_use: str
    when_to_use_fr: str | None
    related_exercise_ids: list[str]


@router.get("", response_model=list[FunctionReferenceSummary])
def list_functions(
    repo: FunctionReferenceRepository = Depends(get_repository),
) -> list[FunctionReferenceSummary]:
    """List every function reference, alphabetically."""
    return [
        FunctionReferenceSummary(id=f.id, name=f.name, name_fr=f.name_fr)
        for f in repo.list_all()
    ]


@router.get("/{function_id}", response_model=FunctionReferenceDetail)
def get_function(
    function_id: str, repo: FunctionReferenceRepository = Depends(get_repository)
) -> FunctionReferenceDetail:
    """Return a single function reference."""
    function = repo.get(function_id)
    if function is None:
        raise HTTPException(status_code=404, detail="Function reference not found")
    return FunctionReferenceDetail(
        id=function.id,
        name=function.name,
        name_fr=function.name_fr,
        what_it_does=function.what_it_does,
        what_it_does_fr=function.what_it_does_fr,
        syntax=function.syntax,
        parameters=function.parameters,
        parameters_fr=function.parameters_fr,
        return_value=function.return_value,
        return_value_fr=function.return_value_fr,
        example=function.example,
        example_output=function.example_output,
        common_mistakes=function.common_mistakes,
        common_mistakes_fr=function.common_mistakes_fr,
        when_to_use=function.when_to_use,
        when_to_use_fr=function.when_to_use_fr,
        related_exercise_ids=function.related_exercise_ids,
    )
