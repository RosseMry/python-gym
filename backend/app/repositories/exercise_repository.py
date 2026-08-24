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
    columns = row.keys()
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
        # Sprint 2 metadata columns. Guarded with .get()-style checks so
        # this keeps working against a connection whose schema migration
        # hasn't run yet (defensive, not expected in normal operation).
        track=row["track"] if "track" in columns else "python",
        source=row["source"] if "source" in columns else "progressive_python",
        skills=json.loads(row["skills"]) if "skills" in columns else [],
        prerequisites=(
            json.loads(row["prerequisites"]) if "prerequisites" in columns else []
        ),
        resources=json.loads(row["resources"]) if "resources" in columns else [],
        validation_profile=(
            row["validation_profile"]
            if "validation_profile" in columns
            else "standard_python"
        ),
        exercise_type=(
            row["exercise_type"] if "exercise_type" in columns else "function"
        ),
        exercise_status=(
            row["exercise_status"] if "exercise_status" in columns else "active"
        ),
        day=row["day"] if "day" in columns else None,
        level=row["level"] if "level" in columns else None,
        title_fr=row["title_fr"] if "title_fr" in columns else None,
        description_fr=row["description_fr"] if "description_fr" in columns else None,
        examples_fr=row["examples_fr"] if "examples_fr" in columns else None,
        expected_behavior_fr=(
            row["expected_behavior_fr"] if "expected_behavior_fr" in columns else None
        ),
        explanation_fr=row["explanation_fr"] if "explanation_fr" in columns else None,
        hints_fr=(
            json.loads(row["hints_fr"])
            if "hints_fr" in columns and row["hints_fr"]
            else None
        ),
        hint_functions=(
            json.loads(row["hint_functions"])
            if "hint_functions" in columns and row["hint_functions"]
            else None
        ),
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
                solution, explanation, concepts, track, source, skills,
                prerequisites, resources, validation_profile,
                exercise_type, exercise_status, day, level, title_fr,
                description_fr, examples_fr, expected_behavior_fr,
                explanation_fr, hints_fr, hint_functions
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
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
                concepts=excluded.concepts,
                track=excluded.track,
                source=excluded.source,
                skills=excluded.skills,
                prerequisites=excluded.prerequisites,
                resources=excluded.resources,
                validation_profile=excluded.validation_profile,
                exercise_type=excluded.exercise_type,
                exercise_status=excluded.exercise_status,
                day=excluded.day,
                level=excluded.level,
                title_fr=excluded.title_fr,
                description_fr=excluded.description_fr,
                examples_fr=excluded.examples_fr,
                expected_behavior_fr=excluded.expected_behavior_fr,
                explanation_fr=excluded.explanation_fr,
                hints_fr=excluded.hints_fr,
                hint_functions=excluded.hint_functions
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
                exercise.track,
                exercise.source,
                json.dumps(exercise.skills),
                json.dumps(exercise.prerequisites),
                json.dumps(exercise.resources),
                exercise.validation_profile,
                exercise.exercise_type,
                exercise.exercise_status,
                exercise.day,
                exercise.level,
                exercise.title_fr,
                exercise.description_fr,
                exercise.examples_fr,
                exercise.expected_behavior_fr,
                exercise.explanation_fr,
                json.dumps(exercise.hints_fr) if exercise.hints_fr else None,
                (
                    json.dumps(exercise.hint_functions)
                    if exercise.hint_functions
                    else None
                ),
            ),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO progress (exercise_id, status) VALUES (?, ?)",
            (exercise.id, ExerciseStatus.NEW.value),
        )
        self._conn.commit()

    def list_all(
        self, module: str | None = None, include_excluded: bool = False
    ) -> list[Exercise]:
        """Return exercises, optionally filtered by module.

        Excluded exercises (spec section 33, e.g. the 42 compression
        exercise) are hidden from normal listings by default so they
        never appear in the learning path or count as pending.
        """
        clauses = []
        params: list[str] = []
        if module:
            clauses.append("module = ?")
            params.append(module)
        if not include_excluded:
            clauses.append("exercise_status != 'excluded'")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._conn.execute(
            f"SELECT * FROM exercises {where} ORDER BY module, difficulty, id",
            params,
        ).fetchall()
        return [_row_to_exercise(r) for r in rows]

    def list_by_source(self, source: str) -> list[Exercise]:
        """Return active exercises for one or more content sources.

        ``source`` accepts a comma-separated list (e.g.
        "foundations,progressive_python,python_gym") so the frontend's
        merged "Progressive -> Foundations" nav item can fetch several
        sources in one request instead of stitching results together
        client-side.
        """
        sources = [s.strip() for s in source.split(",") if s.strip()]
        placeholders = ",".join("?" for _ in sources)
        rows = self._conn.execute(
            f"""
            SELECT * FROM exercises
            WHERE source IN ({placeholders}) AND exercise_status != 'excluded'
            ORDER BY difficulty, id
            """,
            sources,
        ).fetchall()
        return [_row_to_exercise(r) for r in rows]

    def get(self, exercise_id: str) -> Exercise | None:
        """Return a single exercise by id, or None if it does not exist."""
        row = self._conn.execute(
            "SELECT * FROM exercises WHERE id = ?", (exercise_id,)
        ).fetchone()
        return _row_to_exercise(row) if row else None

    def resolve_prerequisites(self, exercise_ids: list[str]) -> list[dict]:
        """Resolve prerequisite ids into ``{id, title, solved}`` for display.

        Basic learning path (Sprint 3): prerequisites were already
        stored as raw ids since Sprint 2 but never resolved into
        anything a student could act on.
        """
        if not exercise_ids:
            return []
        placeholders = ",".join("?" for _ in exercise_ids)
        titles = {
            row["id"]: row["title"]
            for row in self._conn.execute(
                f"SELECT id, title FROM exercises WHERE id IN ({placeholders})",
                exercise_ids,
            ).fetchall()
        }
        solved_family = (
            ExerciseStatus.SOLVED.value,
            ExerciseStatus.SOLVED_WITH_HINT.value,
            ExerciseStatus.SOLVED_AFTER_SOLUTION.value,
            ExerciseStatus.SOLVED_TO_REPEAT.value,
            ExerciseStatus.MASTERED.value,
        )
        solved_placeholders = ",".join("?" for _ in solved_family)
        solved_ids = {
            row["exercise_id"]
            for row in self._conn.execute(
                f"""
                SELECT exercise_id FROM progress
                WHERE exercise_id IN ({placeholders})
                AND status IN ({solved_placeholders})
                """,
                [*exercise_ids, *solved_family],
            ).fetchall()
        }
        return [
            {
                "id": prereq_id,
                "title": titles.get(prereq_id, prereq_id),
                "solved": prereq_id in solved_ids,
            }
            for prereq_id in exercise_ids
        ]

    def get_next_unsolved(self, source: str | None = None) -> Exercise | None:
        """First not-yet-solved exercise, optionally within one source.

        Deliberately simple catalog-order recommendation, not an
        adaptive/scoring engine (Sprint 3 explicitly defers that).
        """
        solved_family = (
            ExerciseStatus.SOLVED.value,
            ExerciseStatus.SOLVED_WITH_HINT.value,
            ExerciseStatus.SOLVED_AFTER_SOLUTION.value,
            ExerciseStatus.SOLVED_TO_REPEAT.value,
            ExerciseStatus.MASTERED.value,
        )
        solved_placeholders = ",".join("?" for _ in solved_family)
        clauses = [
            "exercises.exercise_status NOT IN ('excluded', 'locked')",
            f"(progress.status IS NULL OR progress.status NOT IN "
            f"({solved_placeholders}))",
        ]
        params: list[str] = list(solved_family)
        if source:
            clauses.append("exercises.source = ?")
            params.append(source)
        where = " AND ".join(clauses)
        row = self._conn.execute(
            f"""
            SELECT exercises.* FROM exercises
            LEFT JOIN progress ON progress.exercise_id = exercises.id
            WHERE {where}
            ORDER BY exercises.module, exercises.difficulty, exercises.id
            LIMIT 1
            """,
            params,
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

    def list_repeat_queue(self) -> list[Exercise]:
        """Return exercises the student explicitly marked to repeat later.

        Sprint 2 spec section 5 - these are surfaced separately from the
        main exercise list so the student can find and re-practice them.
        """
        rows = self._conn.execute(
            """
            SELECT exercises.* FROM exercises
            JOIN progress ON progress.exercise_id = exercises.id
            WHERE progress.status = ?
            ORDER BY progress.last_submitted_at DESC
            """,
            (ExerciseStatus.SOLVED_TO_REPEAT.value,),
        ).fetchall()
        return [_row_to_exercise(r) for r in rows]

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
        status: str = "failed",
        hints_used_snapshot: int = 0,
        solution_revealed_snapshot: bool = False,
    ) -> None:
        """Log a single submission attempt for later analytics.

        Sprint 2 spec section 7 - attempts should retain enough context
        (hints used, solution-revealed state) to be interpreted later,
        not just a pass/fail flag.
        """
        self._conn.execute(
            """
            INSERT INTO submissions
                (exercise_id, code, passed, tests_total, tests_passed,
                 status, hints_used_snapshot, solution_revealed_snapshot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                exercise_id,
                code,
                int(passed),
                tests_total,
                tests_passed,
                status,
                hints_used_snapshot,
                int(solution_revealed_snapshot),
            ),
        )
        self._conn.commit()

    def save_explanation(self, exercise_id: str, text: str) -> None:
        """Store the student's own explanation of their solution."""
        self._conn.execute(
            "INSERT INTO explanations (exercise_id, text) VALUES (?, ?)",
            (exercise_id, text),
        )
        self._conn.commit()
