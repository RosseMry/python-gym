"""HTTP routes for SQL learning notes (Sprint 4, mirrors app.api.notes)."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.sql_notes_repository import SqlNotesRepository

router = APIRouter(prefix="/api/sql/notes", tags=["sql"])


def get_repository() -> Iterator[SqlNotesRepository]:
    """Build a repository with a fresh, request-scoped DB connection."""
    conn = get_connection()
    try:
        yield SqlNotesRepository(conn)
    finally:
        conn.close()


class SqlLearningNoteSummary(BaseModel):
    id: str
    module: str
    title: str
    title_fr: str | None


class SqlLearningNoteDetail(BaseModel):
    id: str
    module: str
    title: str
    title_fr: str | None
    what_is_it: str
    what_is_it_fr: str | None
    why_it_matters: str
    why_it_matters_fr: str | None
    syntax: str
    syntax_fr: str | None
    example: str
    output: str
    common_mistakes: str
    common_mistakes_fr: str | None
    postgres_note: str | None
    mini_exercise: str
    mini_exercise_fr: str | None
    source: str
    related_exercise_ids: list[str]


@router.get("", response_model=list[SqlLearningNoteSummary])
def list_sql_notes(
    repo: SqlNotesRepository = Depends(get_repository),
) -> list[SqlLearningNoteSummary]:
    """List every SQL learning note, in display order."""
    return [
        SqlLearningNoteSummary(
            id=n.id, module=n.module, title=n.title, title_fr=n.title_fr
        )
        for n in repo.list_all()
    ]


@router.get("/{note_id}", response_model=SqlLearningNoteDetail)
def get_sql_note(
    note_id: str, repo: SqlNotesRepository = Depends(get_repository)
) -> SqlLearningNoteDetail:
    """Return a single SQL learning note."""
    note = repo.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="SQL learning note not found")
    return SqlLearningNoteDetail(
        id=note.id,
        module=note.module,
        title=note.title,
        title_fr=note.title_fr,
        what_is_it=note.what_is_it,
        what_is_it_fr=note.what_is_it_fr,
        why_it_matters=note.why_it_matters,
        why_it_matters_fr=note.why_it_matters_fr,
        syntax=note.syntax,
        syntax_fr=note.syntax_fr,
        example=note.example,
        output=note.output,
        common_mistakes=note.common_mistakes,
        common_mistakes_fr=note.common_mistakes_fr,
        postgres_note=note.postgres_note,
        mini_exercise=note.mini_exercise,
        mini_exercise_fr=note.mini_exercise_fr,
        source=note.source,
        related_exercise_ids=note.related_exercise_ids,
    )
