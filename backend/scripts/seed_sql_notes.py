"""Loads every SQL learning note JSON file under sql_notes/ into the DB.

Run with:

    uv run python scripts/seed_sql_notes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import SqlLearningNote  # noqa: E402
from app.models.database import get_connection, init_db  # noqa: E402
from app.repositories.sql_notes_repository import SqlNotesRepository  # noqa: E402

NOTES_DIR = BACKEND_DIR.parent / "sql_notes"


def load_note(path: Path) -> SqlLearningNote:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SqlLearningNote(
        id=data["id"],
        module=data["module"],
        title=data["title"],
        display_order=data["display_order"],
        what_is_it=data["what_is_it"],
        why_it_matters=data["why_it_matters"],
        syntax=data["syntax"],
        example=data["example"],
        output=data["output"],
        common_mistakes=data["common_mistakes"],
        mini_exercise=data["mini_exercise"],
        postgres_note=data.get("postgres_note"),
        source=data.get("source", "freecodecamp"),
        related_exercise_ids=data.get("related_exercise_ids", []),
        title_fr=data.get("title_fr"),
        what_is_it_fr=data.get("what_is_it_fr"),
        why_it_matters_fr=data.get("why_it_matters_fr"),
        syntax_fr=data.get("syntax_fr"),
        common_mistakes_fr=data.get("common_mistakes_fr"),
        mini_exercise_fr=data.get("mini_exercise_fr"),
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = SqlNotesRepository(conn)

    json_files = sorted(NOTES_DIR.glob("*.json"))
    if not json_files:
        print(f"No SQL learning note files found under {NOTES_DIR}")
        return

    for path in json_files:
        note = load_note(path)
        repo.upsert(note)
        print(f"seeded sql note {note.id} ({note.module})")

    print(f"\nSeeded {len(json_files)} SQL learning notes.")


if __name__ == "__main__":
    main()
