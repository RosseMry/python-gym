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
        # Sprint 2 metadata - default to Sprint 1's implicit values when
        # a JSON file predates these fields.
        track=data.get("track", "python"),
        source=data.get("source", "progressive_python"),
        skills=data.get("skills", []),
        prerequisites=data.get("prerequisites", []),
        resources=data.get("resources", []),
        validation_profile=data.get("validation_profile", "standard_python"),
        exercise_type=data.get("exercise_type", "function"),
        exercise_status=data.get("exercise_status", "active"),
        # Sprint 3 correction - only meaningful for 30_days_of_python.
        day=data.get("day"),
        level=data.get("level"),
        # Sprint 3 French translations - all optional, absent means
        # "not translated yet" (frontend falls back to English).
        title_fr=data.get("title_fr"),
        description_fr=data.get("description_fr"),
        examples_fr=data.get("examples_fr"),
        expected_behavior_fr=data.get("expected_behavior_fr"),
        explanation_fr=data.get("explanation_fr"),
        hints_fr=data.get("hints_fr"),
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
        print(f"seeded {exercise.id} ({exercise.source}/{exercise.module})")

    print(f"\nSeeded {len(json_files)} exercises.")
    by_source: dict[str, int] = {}
    for path in json_files:
        source = load_exercise(path).source
        by_source[source] = by_source.get(source, 0) + 1
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count}")


if __name__ == "__main__":
    main()
