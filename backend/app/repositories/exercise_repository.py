"""Data access layer for exercises and progress.

No business logic lives here - only reading and writing rows.
"""

from __future__ import annotations

import json
import sqlite3

from app.domain.models import (
    Exercise,
    ExerciseStatus,
    HiddenTest,
    ProgressEntry,
)


def _row_to_exercise(row: sqlite3.Row) -> Exercise:
    return Exercise(
        id=row["id"],
        module=row["module"],
        difficulty=row["difficulty"],
        title=row["title"],
        description=row["description"],
        examples=row["examples"],
        starter_code=row["starter_code"],
        hints=json.loads(row["hints"]),
        expected_behavior=row["expected_behavior"],
        hidden_tests=[HiddenTest(**t) for t in json.loads(row["hidden_tests"])],
        solution=row["solution"],
        explanation=row["explanation"],
        concepts=json.loads(row["concepts"]),
    )


class ExerciseRepository:
    """Reads and writes exercises, using an injected SQLite connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert(self, exercise: Exercise) -> None:
        """Insert or replace a single exercise (used by the seed script)."""
        self._conn.execute(
            """
            INSERT INTO exercises (
                id, module, difficulty, title, description, examples,
                starter_code, hints, expected_behavior, hidden_tests,
                solution, explanation, concepts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                module=excluded.module,
                difficulty=excluded.difficulty,
                title=excluded.title,
                description=excluded.description,
                examples=excluded.examples,
                starter_code=excluded.starter_code,
                hints=excluded.hints,
                expected_behavior=excluded.expected_behavior,
                hidden_tests=excluded.hidden_tests,
                solution=excluded.solution,
                explanation=excluded.explanation,
                concepts=excluded.concepts
            """,
            (
                exercise.id,
                exercise.module,
                exercise.difficulty,
                exercise.title,
                exercise.description,
                exercise.examples,
                exercise.starter_code,
                json.dumps(exercise.hints),
                exercise.expected_behavior,
                json.dumps([t.__dict__ for t in exercise.hidden_tests]),
                exercise.solution,
                exercise.explanation,
                json.dumps(exercise.concepts),
            ),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO progress (exercise_id, status) VALUES (?, ?)",
            (exercise.id, ExerciseStatus.NEW.value),
        )
        self._conn.commit()

    def list_all(self, module: str | None = None) -> list[Exercise]:
        """Return exercises, optionally filtered by module."""
        if module:
            rows = self._conn.execute(
                "SELECT * FROM exercises WHERE module = ? ORDER BY difficulty, id",
                (module,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM exercises ORDER BY module, difficulty, id"
            ).fetchall()
        return [_row_to_exercise(r) for r in rows]

    def get(self, exercise_id: str) -> Exercise | None:
        """Return a single exercise by id, or None if it does not exist."""
        row = self._conn.execute(
            "SELECT * FROM exercises WHERE id = ?", (exercise_id,)
        ).fetchone()
        return _row_to_exercise(row) if row else None

    def get_progress(self, exercise_id: str) -> ProgressEntry | None:
        """Return the progress record for a single exercise."""
        row = self._conn.execute(
            "SELECT * FROM progress WHERE exercise_id = ?", (exercise_id,)
        ).fetchone()
        if not row:
            return None
        return ProgressEntry(
            exercise_id=row["exercise_id"],
            status=ExerciseStatus(row["status"]),
            attempts=row["attempts"],
            hints_used=row["hints_used"],
            solution_revealed=bool(row["solution_revealed"]),
            last_submitted_at=row["last_submitted_at"],
        )

    def list_progress(self) -> list[ProgressEntry]:
        """Return progress records for every exercise."""
        rows = self._conn.execute("SELECT * FROM progress").fetchall()
        return [
            ProgressEntry(
                exercise_id=r["exercise_id"],
                status=ExerciseStatus(r["status"]),
                attempts=r["attempts"],
                hints_used=r["hints_used"],
                solution_revealed=bool(r["solution_revealed"]),
                last_submitted_at=r["last_submitted_at"],
            )
            for r in rows
        ]

    def save_progress(self, progress: ProgressEntry) -> None:
        """Persist an updated progress record."""
        self._conn.execute(
            """
            UPDATE progress
            SET status = ?, attempts = ?, hints_used = ?,
                solution_revealed = ?, last_submitted_at = datetime('now')
            WHERE exercise_id = ?
            """,
            (
                progress.status.value,
                progress.attempts,
                progress.hints_used,
                int(progress.solution_revealed),
                progress.exercise_id,
            ),
        )
        self._conn.commit()

    def record_submission(
        self,
        exercise_id: str,
        code: str,
        passed: bool,
        tests_total: int,
        tests_passed: int,
    ) -> None:
        """Log a single submission attempt for later analytics."""
        self._conn.execute(
            """
            INSERT INTO submissions
                (exercise_id, code, passed, tests_total, tests_passed)
            VALUES (?, ?, ?, ?, ?)
            """,
            (exercise_id, code, int(passed), tests_total, tests_passed),
        )
        self._conn.commit()

    def save_explanation(self, exercise_id: str, text: str) -> None:
        """Store the student's own explanation of their solution."""
        self._conn.execute(
            "INSERT INTO explanations (exercise_id, text) VALUES (?, ?)",
            (exercise_id, text),
        )
        self._conn.commit()
