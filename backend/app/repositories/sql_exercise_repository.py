"""Data access layer for SQL exercises and progress (Sprint 4).

Mirrors ExerciseRepository's shape and conventions, kept as its own
class rather than folded into ExerciseRepository since SQL exercises
are a distinct domain type (SqlExercise, not Exercise) with their own
table and grading path (see sql_execution_service).
"""

from __future__ import annotations

import json
import sqlite3

from app.domain.models import ExerciseStatus, ProgressEntry, SqlExercise, SqlHiddenTest


def _row_to_sql_exercise(row: sqlite3.Row) -> SqlExercise:
    return SqlExercise(
        id=row["id"],
        module=row["module"],
        difficulty=row["difficulty"],
        title=row["title"],
        description=row["description"],
        starter_query=row["starter_query"],
        hints=json.loads(row["hints"]),
        expected_behavior=row["expected_behavior"],
        hidden_tests=[SqlHiddenTest(**t) for t in json.loads(row["hidden_tests"])],
        solution=row["solution"],
        explanation=row["explanation"],
        concepts=json.loads(row["concepts"]),
        skills=json.loads(row["skills"]),
        source=row["source"],
        postgres_note=row["postgres_note"],
        prerequisites=json.loads(row["prerequisites"]),
        exercise_status=row["exercise_status"],
        title_fr=row["title_fr"],
        description_fr=row["description_fr"],
        explanation_fr=row["explanation_fr"],
        hints_fr=json.loads(row["hints_fr"]) if row["hints_fr"] else None,
        schema=row["schema"],
        project=row["project"],
        part=row["part"],
    )


class SqlExerciseRepository:
    """Reads and writes SQL exercises and their progress."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert(self, exercise: SqlExercise) -> None:
        """Insert or replace a single SQL exercise (used by the seed script)."""
        self._conn.execute(
            """
            INSERT INTO sql_exercises (
                id, module, difficulty, title, description, starter_query,
                hints, expected_behavior, hidden_tests, solution,
                explanation, concepts, skills, source, postgres_note,
                prerequisites, exercise_status, title_fr, description_fr,
                explanation_fr, hints_fr, schema, project, part
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT(id) DO UPDATE SET
                module=excluded.module,
                difficulty=excluded.difficulty,
                title=excluded.title,
                description=excluded.description,
                starter_query=excluded.starter_query,
                hints=excluded.hints,
                expected_behavior=excluded.expected_behavior,
                hidden_tests=excluded.hidden_tests,
                solution=excluded.solution,
                explanation=excluded.explanation,
                concepts=excluded.concepts,
                skills=excluded.skills,
                source=excluded.source,
                postgres_note=excluded.postgres_note,
                prerequisites=excluded.prerequisites,
                exercise_status=excluded.exercise_status,
                title_fr=excluded.title_fr,
                description_fr=excluded.description_fr,
                explanation_fr=excluded.explanation_fr,
                hints_fr=excluded.hints_fr,
                schema=excluded.schema,
                project=excluded.project,
                part=excluded.part
            """,
            (
                exercise.id,
                exercise.module,
                exercise.difficulty,
                exercise.title,
                exercise.description,
                exercise.starter_query,
                json.dumps(exercise.hints),
                exercise.expected_behavior,
                json.dumps([t.__dict__ for t in exercise.hidden_tests]),
                exercise.solution,
                exercise.explanation,
                json.dumps(exercise.concepts),
                json.dumps(exercise.skills),
                exercise.source,
                exercise.postgres_note,
                json.dumps(exercise.prerequisites),
                exercise.exercise_status,
                exercise.title_fr,
                exercise.description_fr,
                exercise.explanation_fr,
                json.dumps(exercise.hints_fr) if exercise.hints_fr else None,
                exercise.schema,
                exercise.project,
                exercise.part,
            ),
        )
        self._conn.commit()

    def get(self, exercise_id: str) -> SqlExercise | None:
        row = self._conn.execute(
            "SELECT * FROM sql_exercises WHERE id = ?", (exercise_id,)
        ).fetchone()
        return _row_to_sql_exercise(row) if row else None

    def list_all(
        self, module: str | None = None, project: str | None = None
    ) -> list[SqlExercise]:
        if project:
            rows = self._conn.execute(
                "SELECT * FROM sql_exercises WHERE project = ? "
                "ORDER BY part, difficulty, id",
                (project,),
            ).fetchall()
        elif module:
            rows = self._conn.execute(
                "SELECT * FROM sql_exercises WHERE module = ? ORDER BY difficulty, id",
                (module,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM sql_exercises ORDER BY module, difficulty, id"
            ).fetchall()
        return [_row_to_sql_exercise(row) for row in rows]

    def list_projects(self) -> list[str]:
        """Distinct Mini Project ids, in first-seen (part/id) order."""
        rows = self._conn.execute(
            "SELECT DISTINCT project FROM sql_exercises "
            "WHERE project IS NOT NULL ORDER BY project"
        ).fetchall()
        return [row["project"] for row in rows]

    def get_progress(self, exercise_id: str) -> ProgressEntry:
        row = self._conn.execute(
            "SELECT * FROM sql_progress WHERE exercise_id = ?", (exercise_id,)
        ).fetchone()
        if row is None:
            return ProgressEntry(
                exercise_id=exercise_id,
                status=ExerciseStatus.NEW,
                attempts=0,
                hints_used=0,
                solution_revealed=False,
            )
        return ProgressEntry(
            exercise_id=row["exercise_id"],
            status=ExerciseStatus(row["status"]),
            attempts=row["attempts"],
            hints_used=row["hints_used"],
            solution_revealed=bool(row["solution_revealed"]),
            last_submitted_at=row["last_submitted_at"],
        )

    def save_progress(self, progress: ProgressEntry) -> None:
        self._conn.execute(
            """
            INSERT INTO sql_progress (
                exercise_id, status, attempts, hints_used,
                solution_revealed, last_submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(exercise_id) DO UPDATE SET
                status=excluded.status,
                attempts=excluded.attempts,
                hints_used=excluded.hints_used,
                solution_revealed=excluded.solution_revealed,
                last_submitted_at=excluded.last_submitted_at
            """,
            (
                progress.exercise_id,
                progress.status.value,
                progress.attempts,
                progress.hints_used,
                int(progress.solution_revealed),
                progress.last_submitted_at,
            ),
        )
        self._conn.commit()

    def record_submission(
        self,
        exercise_id: str,
        query: str,
        passed: bool,
        tests_total: int,
        tests_passed: int,
        status: str,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO sql_submissions (
                exercise_id, query, passed, tests_total, tests_passed, status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (exercise_id, query, int(passed), tests_total, tests_passed, status),
        )
        self._conn.commit()

    def list_progress(self) -> list[ProgressEntry]:
        rows = self._conn.execute("SELECT * FROM sql_progress").fetchall()
        return [
            ProgressEntry(
                exercise_id=row["exercise_id"],
                status=ExerciseStatus(row["status"]),
                attempts=row["attempts"],
                hints_used=row["hints_used"],
                solution_revealed=bool(row["solution_revealed"]),
                last_submitted_at=row["last_submitted_at"],
            )
            for row in rows
        ]
