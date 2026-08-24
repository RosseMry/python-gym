"""Data access layer for the Function Reference catalog.

No business logic lives here - only reading and writing rows, mirroring
NotesRepository's shape.
"""

from __future__ import annotations

import json
import sqlite3

from app.domain.models import FunctionReference


def _row_to_function(row: sqlite3.Row) -> FunctionReference:
    return FunctionReference(
        id=row["id"],
        name=row["name"],
        what_it_does=row["what_it_does"],
        syntax=row["syntax"],
        parameters=row["parameters"],
        return_value=row["return_value"],
        example=row["example"],
        example_output=row["example_output"],
        common_mistakes=row["common_mistakes"],
        when_to_use=row["when_to_use"],
        related_exercise_ids=json.loads(row["related_exercise_ids"]),
        name_fr=row["name_fr"],
        what_it_does_fr=row["what_it_does_fr"],
        parameters_fr=row["parameters_fr"],
        return_value_fr=row["return_value_fr"],
        common_mistakes_fr=row["common_mistakes_fr"],
        when_to_use_fr=row["when_to_use_fr"],
    )


class FunctionReferenceRepository:
    """Reads and writes function references, using an injected connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert(self, function: FunctionReference) -> None:
        """Insert or replace one function reference (used by the seed script)."""
        self._conn.execute(
            """
            INSERT INTO function_references (
                id, name, what_it_does, syntax, parameters, return_value,
                example, example_output, common_mistakes, when_to_use,
                related_exercise_ids, name_fr, what_it_does_fr,
                parameters_fr, return_value_fr, common_mistakes_fr,
                when_to_use_fr
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                what_it_does=excluded.what_it_does,
                syntax=excluded.syntax,
                parameters=excluded.parameters,
                return_value=excluded.return_value,
                example=excluded.example,
                example_output=excluded.example_output,
                common_mistakes=excluded.common_mistakes,
                when_to_use=excluded.when_to_use,
                related_exercise_ids=excluded.related_exercise_ids,
                name_fr=excluded.name_fr,
                what_it_does_fr=excluded.what_it_does_fr,
                parameters_fr=excluded.parameters_fr,
                return_value_fr=excluded.return_value_fr,
                common_mistakes_fr=excluded.common_mistakes_fr,
                when_to_use_fr=excluded.when_to_use_fr
            """,
            (
                function.id,
                function.name,
                function.what_it_does,
                function.syntax,
                function.parameters,
                function.return_value,
                function.example,
                function.example_output,
                function.common_mistakes,
                function.when_to_use,
                json.dumps(function.related_exercise_ids),
                function.name_fr,
                function.what_it_does_fr,
                function.parameters_fr,
                function.return_value_fr,
                function.common_mistakes_fr,
                function.when_to_use_fr,
            ),
        )
        self._conn.commit()

    def list_all(self) -> list[FunctionReference]:
        """Return every function reference, alphabetically by name."""
        rows = self._conn.execute(
            "SELECT * FROM function_references ORDER BY name"
        ).fetchall()
        return [_row_to_function(r) for r in rows]

    def get(self, function_id: str) -> FunctionReference | None:
        """Return a single function reference by id, or None if missing."""
        row = self._conn.execute(
            "SELECT * FROM function_references WHERE id = ?", (function_id,)
        ).fetchone()
        return _row_to_function(row) if row else None
