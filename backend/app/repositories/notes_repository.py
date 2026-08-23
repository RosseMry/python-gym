"""Data access layer for learning notes.

No business logic lives here - only reading and writing rows, mirroring
ExerciseRepository's shape.
"""

from __future__ import annotations

import json
import sqlite3

from app.domain.models import LearningNote


def _row_to_note(row: sqlite3.Row) -> LearningNote:
    return LearningNote(
        id=row["id"],
        module=row["module"],
        title=row["title"],
        display_order=row["display_order"],
        explanation=row["explanation"],
        syntax=row["syntax"],
        examples=row["examples"],
        common_mistakes=row["common_mistakes"],
        mini_exercise=row["mini_exercise"],
        related_exercise_ids=json.loads(row["related_exercise_ids"]),
        title_fr=row["title_fr"],
        explanation_fr=row["explanation_fr"],
        syntax_fr=row["syntax_fr"],
        examples_fr=row["examples_fr"],
        common_mistakes_fr=row["common_mistakes_fr"],
        mini_exercise_fr=row["mini_exercise_fr"],
    )


class NotesRepository:
    """Reads and writes learning notes, using an injected SQLite connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert(self, note: LearningNote) -> None:
        """Insert or replace a single learning note (used by the seed script)."""
        self._conn.execute(
            """
            INSERT INTO learning_notes (
                id, module, title, display_order, explanation, syntax,
                examples, common_mistakes, mini_exercise,
                related_exercise_ids, title_fr, explanation_fr,
                syntax_fr, examples_fr, common_mistakes_fr,
                mini_exercise_fr
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                module=excluded.module,
                title=excluded.title,
                display_order=excluded.display_order,
                explanation=excluded.explanation,
                syntax=excluded.syntax,
                examples=excluded.examples,
                common_mistakes=excluded.common_mistakes,
                mini_exercise=excluded.mini_exercise,
                related_exercise_ids=excluded.related_exercise_ids,
                title_fr=excluded.title_fr,
                explanation_fr=excluded.explanation_fr,
                syntax_fr=excluded.syntax_fr,
                examples_fr=excluded.examples_fr,
                common_mistakes_fr=excluded.common_mistakes_fr,
                mini_exercise_fr=excluded.mini_exercise_fr
            """,
            (
                note.id,
                note.module,
                note.title,
                note.display_order,
                note.explanation,
                note.syntax,
                note.examples,
                note.common_mistakes,
                note.mini_exercise,
                json.dumps(note.related_exercise_ids),
                note.title_fr,
                note.explanation_fr,
                note.syntax_fr,
                note.examples_fr,
                note.common_mistakes_fr,
                note.mini_exercise_fr,
            ),
        )
        self._conn.commit()

    def list_all(self) -> list[LearningNote]:
        """Return every learning note, ordered for display."""
        rows = self._conn.execute(
            "SELECT * FROM learning_notes ORDER BY display_order, id"
        ).fetchall()
        return [_row_to_note(r) for r in rows]

    def get(self, note_id: str) -> LearningNote | None:
        """Return a single learning note by id, or None if it does not exist."""
        row = self._conn.execute(
            "SELECT * FROM learning_notes WHERE id = ?", (note_id,)
        ).fetchone()
        return _row_to_note(row) if row else None
