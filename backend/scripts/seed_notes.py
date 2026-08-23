"""Loads every learning note JSON file under notes/ into the SQLite DB.

Run with:

    uv run python scripts/seed_notes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import LearningNote  # noqa: E402
from app.models.database import get_connection, init_db  # noqa: E402
from app.repositories.notes_repository import NotesRepository  # noqa: E402

NOTES_DIR = BACKEND_DIR.parent / "notes"


def load_note(path: Path) -> LearningNote:
    data = json.loads(path.read_text(encoding="utf-8"))
    return LearningNote(
        id=data["id"],
        module=data["module"],
        title=data["title"],
        display_order=data["display_order"],
        explanation=data["explanation"],
        syntax=data["syntax"],
        examples=data["examples"],
        common_mistakes=data["common_mistakes"],
        mini_exercise=data["mini_exercise"],
        related_exercise_ids=data.get("related_exercise_ids", []),
        title_fr=data.get("title_fr"),
        explanation_fr=data.get("explanation_fr"),
        syntax_fr=data.get("syntax_fr"),
        examples_fr=data.get("examples_fr"),
        common_mistakes_fr=data.get("common_mistakes_fr"),
        mini_exercise_fr=data.get("mini_exercise_fr"),
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = NotesRepository(conn)

    json_files = sorted(NOTES_DIR.glob("*.json"))
    if not json_files:
        print(f"No learning note files found under {NOTES_DIR}")
        return

    for path in json_files:
        note = load_note(path)
        repo.upsert(note)
        print(f"seeded note {note.id} ({note.module})")

    print(f"\nSeeded {len(json_files)} learning notes.")


if __name__ == "__main__":
    main()
