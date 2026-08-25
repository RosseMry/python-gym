"""Loads every SQL exercise JSON file under sql_exercises/ into the DB.

Run with:

    uv run python scripts/seed_sql.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import SqlExercise, SqlHiddenTest  # noqa: E402
from app.models.database import get_connection, init_db  # noqa: E402
from app.repositories.sql_exercise_repository import SqlExerciseRepository  # noqa: E402

EXERCISES_DIR = BACKEND_DIR.parent / "sql_exercises"


def load_exercise(path: Path) -> SqlExercise:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SqlExercise(
        id=data["id"],
        module=data["module"],
        difficulty=data["difficulty"],
        title=data["title"],
        description=data["description"],
        starter_query=data["starter_query"],
        hints=data["hints"],
        expected_behavior=data["expected_behavior"],
        hidden_tests=[SqlHiddenTest(**t) for t in data["hidden_tests"]],
        solution=data["solution"],
        explanation=data["explanation"],
        concepts=data.get("concepts", []),
        skills=data.get("skills", []),
        source=data.get("source", "python_gym_sql"),
        postgres_note=data.get("postgres_note"),
        prerequisites=data.get("prerequisites", []),
        exercise_status=data.get("exercise_status", "active"),
        title_fr=data.get("title_fr"),
        description_fr=data.get("description_fr"),
        explanation_fr=data.get("explanation_fr"),
        hints_fr=data.get("hints_fr"),
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = SqlExerciseRepository(conn)

    json_files = sorted(EXERCISES_DIR.glob("**/*.json"))
    if not json_files:
        print(f"No SQL exercise files found under {EXERCISES_DIR}")
        return

    exercises = [load_exercise(path) for path in json_files]
    seen_ids: dict[str, Path] = {}
    for path, exercise in zip(json_files, exercises):
        if exercise.id in seen_ids:
            raise ValueError(
                f"Duplicate SQL exercise id {exercise.id!r} in {path} "
                f"(already defined in {seen_ids[exercise.id]})"
            )
        seen_ids[exercise.id] = path

    for exercise in exercises:
        repo.upsert(exercise)
        print(f"seeded {exercise.id} ({exercise.module})")

    print(f"\nSeeded {len(exercises)} SQL exercises.")
    by_module: dict[str, int] = {}
    for exercise in exercises:
        by_module[exercise.module] = by_module.get(exercise.module, 0) + 1
    for module, count in sorted(by_module.items()):
        print(f"  {module}: {count}")


if __name__ == "__main__":
    main()
