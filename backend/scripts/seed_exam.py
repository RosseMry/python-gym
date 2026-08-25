"""Loads every exam question JSON file under exam_questions/ into the DB.

Run with:

    uv run python scripts/seed_exam.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import ExamQuestion, HiddenTest  # noqa: E402
from app.models.database import get_connection, init_db  # noqa: E402
from app.repositories.exam_repository import ExamRepository  # noqa: E402

QUESTIONS_DIR = BACKEND_DIR.parent / "exam_questions"


def load_question(path: Path) -> ExamQuestion:
    data = json.loads(path.read_text(encoding="utf-8"))
    hidden_tests = data.get("hidden_tests")
    return ExamQuestion(
        id=data["id"],
        kind=data["kind"],
        category=data["category"],
        prompt=data["prompt"],
        difficulty=data["difficulty"],
        points=data.get("points", 1),
        code_snippet=data.get("code_snippet"),
        starter_code=data.get("starter_code"),
        choices=data.get("choices"),
        correct_choice=data.get("correct_choice"),
        expected_output=data.get("expected_output"),
        hidden_tests=[HiddenTest(**t) for t in hidden_tests] if hidden_tests else None,
        solution=data.get("solution"),
        explanation=data.get("explanation", ""),
        source=data.get("source", "adapted"),
    )


def main() -> None:
    init_db()
    conn = get_connection()
    repo = ExamRepository(conn)

    json_files = sorted(QUESTIONS_DIR.glob("*.json"))
    if not json_files:
        print(f"No exam question files found under {QUESTIONS_DIR}")
        return

    questions = [load_question(path) for path in json_files]
    seen_ids: dict[str, Path] = {}
    for path, question in zip(json_files, questions):
        if question.id in seen_ids:
            raise ValueError(
                f"Duplicate exam question id {question.id!r} in {path} "
                f"(already defined in {seen_ids[question.id]})"
            )
        seen_ids[question.id] = path

    for question in questions:
        repo.upsert_question(question)
        print(f"seeded {question.id} ({question.kind}/{question.category})")

    print(f"\nSeeded {len(questions)} exam questions.")
    by_kind: dict[str, int] = {}
    for question in questions:
        by_kind[question.kind] = by_kind.get(question.kind, 0) + 1
    for kind, count in sorted(by_kind.items()):
        print(f"  {kind}: {count}")


if __name__ == "__main__":
    main()
