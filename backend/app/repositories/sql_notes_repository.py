"""Data access layer for SQL learning notes (Sprint 4).

Mirrors NotesRepository's shape - SqlLearningNote has a postgres_note
field the Python LearningNote doesn't need, so it's a distinct table
and class rather than reusing NotesRepository directly.
"""

from __future__ import annotations

import json
import sqlite3

from app.domain.models import SqlLearningNote


def _row_to_sql_note(row: sqlite3.Row) -> SqlLearningNote:
    return SqlLearningNote(
        id=row["id"],
        module=row["module"],
        title=row["title"],
        display_order=row["display_order"],
        what_is_it=row["what_is_it"],
        why_it_matters=row["why_it_matters"],
        syntax=row["syntax"],
        example=row["example"],
        output=row["output"],
        common_mistakes=row["common_mistakes"],
        mini_exercise=row["mini_exercise"],
        postgres_note=row["postgres_note"],
        source=row["source"],
        related_exercise_ids=json.loads(row["related_exercise_ids"]),
        title_fr=row["title_fr"],
        what_is_it_fr=row["what_is_it_fr"],
        why_it_matters_fr=row["why_it_matters_fr"],
        syntax_fr=row["syntax_fr"],
        common_mistakes_fr=row["common_mistakes_fr"],
        mini_exercise_fr=row["mini_exercise_fr"],
    )


class SqlNotesRepository:
    """Reads and writes SQL learning notes."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert(self, note: SqlLearningNote) -> None:
        """Insert or replace a single SQL learning note (seed script)."""
        self._conn.execute(
            """
            INSERT INTO sql_learning_notes (
                id, module, title, display_order, what_is_it,
                why_it_matters, syntax, example, output, common_mistakes,
                mini_exercise, postgres_note, source, related_exercise_ids,
                title_fr, what_is_it_fr, why_it_matters_fr, syntax_fr,
                common_mistakes_fr, mini_exercise_fr
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                module=excluded.module,
                title=excluded.title,
                display_order=excluded.display_order,
                what_is_it=excluded.what_is_it,
                why_it_matters=excluded.why_it_matters,
                syntax=excluded.syntax,
                example=excluded.example,
                output=excluded.output,
                common_mistakes=excluded.common_mistakes,
                mini_exercise=excluded.mini_exercise,
                postgres_note=excluded.postgres_note,
                source=excluded.source,
                related_exercise_ids=excluded.related_exercise_ids,
                title_fr=excluded.title_fr,
                what_is_it_fr=excluded.what_is_it_fr,
                why_it_matters_fr=excluded.why_it_matters_fr,
                syntax_fr=excluded.syntax_fr,
                common_mistakes_fr=excluded.common_mistakes_fr,
                mini_exercise_fr=excluded.mini_exercise_fr
            """,
            (
                note.id,
                note.module,
                note.title,
                note.display_order,
                note.what_is_it,
                note.why_it_matters,
                note.syntax,
                note.example,
                note.output,
                note.common_mistakes,
                note.mini_exercise,
                note.postgres_note,
                note.source,
                json.dumps(note.related_exercise_ids),
                note.title_fr,
                note.what_is_it_fr,
                note.why_it_matters_fr,
                note.syntax_fr,
                note.common_mistakes_fr,
                note.mini_exercise_fr,
            ),
        )
        self._conn.commit()

    def list_all(self) -> list[SqlLearningNote]:
        rows = self._conn.execute(
            "SELECT * FROM sql_learning_notes ORDER BY display_order, id"
        ).fetchall()
        return [_row_to_sql_note(r) for r in rows]

    def get(self, note_id: str) -> SqlLearningNote | None:
        row = self._conn.execute(
            "SELECT * FROM sql_learning_notes WHERE id = ?", (note_id,)
        ).fetchone()
        return _row_to_sql_note(row) if row else None
