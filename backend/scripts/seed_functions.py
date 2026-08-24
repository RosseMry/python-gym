"""Loads every function reference JSON file under functions/ into SQLite.

Run with:

    uv run python scripts/seed_functions.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import FunctionReference  # noqa: E402
from app.models.database import get_connection, init_db  # noqa: E402
from app.repositories.function_reference_repository import (  # noqa: E402
    FunctionReferenceRepository,
)

FUNCTIONS_DIR = BACKEND_DIR.parent / "functions"


def load_function(path: Path) -> FunctionReference:
    data = json.loads(path.read_text(encoding="utf-8"))
    return FunctionReference(
        id=data["id"],
        name=data["name"],
        what_it_does=data["what_it_does"],
        syntax=data["syntax"],
        parameters=data["parameters"],
        return_value=data["return_value"],
        example=data["example"],
        example_output=data["example_output"],
        common_mistakes=data["common_mistakes"],
        when_to_use=data["when_to_use"],
        related_exercise_ids=data.get("related_exercise_ids", []),
        name_fr=data.get("name_fr"),
        what_it_does_fr=data.get("what_it_does_fr"),
        parameters_fr=data.get("parameters_fr"),
        return_value_fr=data.get("return_value_fr"),
        common_mistakes_fr=data.get("common_mistakes_fr"),
        when_to_use_fr=data.get("when_to_use_fr"),
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = FunctionReferenceRepository(conn)

    json_files = sorted(FUNCTIONS_DIR.glob("*.json"))
    if not json_files:
        print(f"No function reference files found under {FUNCTIONS_DIR}")
        return

    for path in json_files:
        function = load_function(path)
        repo.upsert(function)
        print(f"seeded function {function.id} ({function.name})")

    print(f"\nSeeded {len(json_files)} function references.")


if __name__ == "__main__":
    main()
