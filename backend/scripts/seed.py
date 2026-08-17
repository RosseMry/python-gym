"""Loads every exercise JSON file under exercises/ into the SQLite DB.

Run with:

    uv run python scripts/seed.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import Exercise, HiddenTest  # noqa: E402
from app.models.database import get_connection, init_db  # noqa: E402
from app.repositories.exercise_repository import ExerciseRepository  # noqa: E402

EXERCISES_DIR = BACKEND_DIR.parent / "exercises"


def load_exercise(path: Path) -> Exercise:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Exercise(
        id=data["id"],
        module=data["module"],
        difficulty=data["difficulty"],
        title=data["title"],
        description=data["description"],
        examples=data["examples"],
        starter_code=data["starter_code"],
        hints=data["hints"],
        expected_behavior=data["expected_behavior"],
        hidden_tests=[HiddenTest(**t) for t in data["hidden_tests"]],
        solution=data["solution"],
        explanation=data["explanation"],
        concepts=data["concepts"],
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = ExerciseRepository(conn)

    json_files = sorted(EXERCISES_DIR.glob("**/*.json"))
    if not json_files:
        print(f"No exercise files found under {EXERCISES_DIR}")
        return

    for path in json_files:
        exercise = load_exercise(path)
        repo.upsert(exercise)
        print(f"seeded {exercise.id} ({exercise.module})")

    print(f"\nSeeded {len(json_files)} exercises.")


if __name__ == "__main__":
    main()
