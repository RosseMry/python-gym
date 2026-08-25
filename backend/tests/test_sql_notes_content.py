"""Tests for the SQL learning notes content under sql_notes/ (Sprint 4)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import SqlLearningNote  # noqa: E402
from scripts.seed_sql import EXERCISES_DIR  # noqa: E402
from scripts.seed_sql import load_exercise as load_sql_exercise  # noqa: E402
from scripts.seed_sql_notes import NOTES_DIR, load_note  # noqa: E402

EXPECTED_MODULES = {
    "foundations",
    "relational",
    "joins",
    "intermediate",
    "window",
    "dbops",
    "views",
    "transactions",
    "indexes",
    "functions",
    "procedures",
    "triggers",
}


@pytest.fixture(scope="module")
def notes() -> list[SqlLearningNote]:
    paths = sorted(NOTES_DIR.glob("*.json"))
    assert paths, f"no SQL note files found under {NOTES_DIR}"
    return [load_note(p) for p in paths]


@pytest.fixture(scope="module")
def valid_exercise_ids() -> set[str]:
    return {load_sql_exercise(p).id for p in EXERCISES_DIR.glob("**/*.json")}


def test_no_duplicate_ids(notes: list[SqlLearningNote]) -> None:
    ids = [n.id for n in notes]
    assert len(ids) == len(set(ids))


def test_every_required_module_has_exactly_one_note(
    notes: list[SqlLearningNote],
) -> None:
    modules = [n.module for n in notes]
    assert set(modules) == EXPECTED_MODULES
    assert len(modules) == len(EXPECTED_MODULES)


def test_display_order_is_unique_and_sequential(
    notes: list[SqlLearningNote],
) -> None:
    orders = sorted(n.display_order for n in notes)
    assert orders == list(range(1, len(notes) + 1))


def test_all_text_fields_are_non_empty(notes: list[SqlLearningNote]) -> None:
    for n in notes:
        for field_name in (
            "what_is_it",
            "why_it_matters",
            "syntax",
            "example",
            "output",
            "common_mistakes",
            "mini_exercise",
        ):
            assert getattr(n, field_name).strip(), (n.id, field_name)


def test_related_exercise_ids_reference_real_exercises(
    notes: list[SqlLearningNote], valid_exercise_ids: set[str]
) -> None:
    for n in notes:
        assert n.related_exercise_ids, n.id
        for exercise_id in n.related_exercise_ids:
            assert exercise_id in valid_exercise_ids, (n.id, exercise_id)


def test_related_exercise_ids_belong_to_the_note_s_own_module(
    notes: list[SqlLearningNote], valid_exercise_ids: set[str]
) -> None:
    for n in notes:
        for exercise_id in n.related_exercise_ids:
            assert exercise_id.startswith(f"sql-{n.module}-"), (n.id, exercise_id)
