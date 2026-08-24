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
        hint_functions=data.get("hint_functions"),
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = ExerciseRepository(conn)

    json_files = sorted(EXERCISES_DIR.glob("**/*.json"))
    if not json_files:
        print(f"No exercise files found under {EXERCISES_DIR}")
        return

    exercises = [load_exercise(path) for path in json_files]

    seen_ids: dict[str, Path] = {}
    for path, exercise in zip(json_files, exercises):
        if exercise.id in seen_ids:
            raise ValueError(
                f"Duplicate exercise id {exercise.id!r} in {path} "
                f"(already defined in {seen_ids[exercise.id]})"
            )
        seen_ids[exercise.id] = path

    for exercise in exercises:
        repo.upsert(exercise)
        print(f"seeded {exercise.id} ({exercise.source}/{exercise.module})")

    print(f"\nSeeded {len(json_files)} exercises.")
    by_source: dict[str, int] = {}
    for exercise in exercises:
        by_source[exercise.source] = by_source.get(exercise.source, 0) + 1
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count}")

    # Seed-integrity audit (spec: compare source vs seed with real
    # numbers, not estimates) - per-day breakdown for 30 Days of Python.
    by_day: dict[int, int] = {}
    for exercise in exercises:
        if exercise.source == "30_days_of_python" and exercise.day is not None:
            by_day[exercise.day] = by_day.get(exercise.day, 0) + 1
    if by_day:
        print("\n  30_days_of_python by day:")
        for day, count in sorted(by_day.items()):
            print(f"    day {day:02d}: {count}")

    # Per-module breakdown for the 42 Piscine, including locked/excluded.
    piscine_by_module: dict[str, dict[str, int]] = {}
    for exercise in exercises:
        if exercise.source != "42_python_piscine":
            continue
        bucket = piscine_by_module.setdefault(
            exercise.module, {"active": 0, "locked": 0, "excluded": 0}
        )
        bucket[exercise.exercise_status] = bucket.get(exercise.exercise_status, 0) + 1
    if piscine_by_module:
        print("\n  42_python_piscine by module:")
        for module, counts in sorted(piscine_by_module.items()):
            print(f"    {module}: {counts}")


if __name__ == "__main__":
    main()
