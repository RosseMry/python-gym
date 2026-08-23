"""HTTP routes for learning notes (Sprint 3: theory pages per topic)."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.notes_repository import NotesRepository

router = APIRouter(prefix="/api/notes", tags=["notes"])


def get_repository() -> Iterator[NotesRepository]:
    """Build a repository with a fresh, request-scoped DB connection."""
    conn = get_connection()
    try:
        yield NotesRepository(conn)
    finally:
        conn.close()


class LearningNoteSummary(BaseModel):
    id: str
    module: str
    title: str
    title_fr: str | None


class LearningNoteDetail(BaseModel):
    id: str
    module: str
    title: str
    title_fr: str | None
    explanation: str
    explanation_fr: str | None
    syntax: str
    syntax_fr: str | None
    examples: str
    examples_fr: str | None
    common_mistakes: str
    common_mistakes_fr: str | None
    mini_exercise: str
    mini_exercise_fr: str | None
    related_exercise_ids: list[str]


@router.get("", response_model=list[LearningNoteSummary])
def list_notes(
    repo: NotesRepository = Depends(get_repository),
) -> list[LearningNoteSummary]:
    """List every learning note, in display order."""
    return [
        LearningNoteSummary(
            id=n.id, module=n.module, title=n.title, title_fr=n.title_fr
        )
        for n in repo.list_all()
    ]


@router.get("/{note_id}", response_model=LearningNoteDetail)
def get_note(
    note_id: str, repo: NotesRepository = Depends(get_repository)
) -> LearningNoteDetail:
    """Return a single learning note."""
    note = repo.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Learning note not found")
    return LearningNoteDetail(
        id=note.id,
        module=note.module,
        title=note.title,
        title_fr=note.title_fr,
        explanation=note.explanation,
        explanation_fr=note.explanation_fr,
        syntax=note.syntax,
        syntax_fr=note.syntax_fr,
        examples=note.examples,
        examples_fr=note.examples_fr,
        common_mistakes=note.common_mistakes,
        common_mistakes_fr=note.common_mistakes_fr,
        mini_exercise=note.mini_exercise,
        mini_exercise_fr=note.mini_exercise_fr,
        related_exercise_ids=note.related_exercise_ids,
    )
