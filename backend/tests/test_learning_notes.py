"""Tests for the Learning Notes feature (Sprint 3)."""

from __future__ import annotations

import sqlite3
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import notes as notes_api
from app.domain.models import LearningNote
from app.main import app
from app.models.database import SCHEMA
from app.repositories.notes_repository import NotesRepository

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from scripts.seed_notes import NOTES_DIR, load_note  # noqa: E402

LISTS_NOTE = LearningNote(
    id="lists",
    module="lists",
    title="Lists",
    display_order=1,
    explanation="A list is an ordered, mutable collection.",
    syntax="numbers = [1, 2, 3]",
    examples="numbers.append(4)",
    common_mistakes="Confusing append and extend.",
    mini_exercise="Predict the output of numbers.append(4).",
    related_exercise_ids=["list-001", "list-002"],
)

DICTS_NOTE = LearningNote(
    id="dictionaries",
    module="dictionaries",
    title="Dictionaries",
    display_order=2,
    explanation="A dictionary stores key-value pairs.",
    syntax="person = {'name': 'Ada'}",
    examples="person['name']",
    common_mistakes="dict[key] raises KeyError if missing.",
    mini_exercise="Predict the output of person.get('age').",
    related_exercise_ids=["piscine-00-sos"],
    title_fr="Dictionnaires",
)


@pytest.fixture()
def notes_conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def notes_repo(notes_conn: sqlite3.Connection) -> NotesRepository:
    repo = NotesRepository(notes_conn)
    repo.upsert(LISTS_NOTE)
    repo.upsert(DICTS_NOTE)
    return repo


def test_list_all_returns_notes_in_display_order(notes_repo: NotesRepository) -> None:
    notes = notes_repo.list_all()
    assert [n.id for n in notes] == ["lists", "dictionaries"]


def test_get_returns_full_note_with_related_exercises(
    notes_repo: NotesRepository,
) -> None:
    note = notes_repo.get("lists")
    assert note is not None
    assert note.title == "Lists"
    assert note.related_exercise_ids == ["list-001", "list-002"]


def test_get_missing_note_returns_none(notes_repo: NotesRepository) -> None:
    assert notes_repo.get("does-not-exist") is None


def test_french_title_falls_back_to_none_when_not_translated(
    notes_repo: NotesRepository,
) -> None:
    lists_note = notes_repo.get("lists")
    dicts_note = notes_repo.get("dictionaries")
    assert lists_note.title_fr is None
    assert dicts_note.title_fr == "Dictionnaires"


def test_upsert_is_idempotent(notes_repo: NotesRepository) -> None:
    notes_repo.upsert(LISTS_NOTE)
    notes = notes_repo.list_all()
    assert len([n for n in notes if n.id == "lists"]) == 1


@pytest.fixture
def client() -> Iterator[TestClient]:
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = NotesRepository(connection)
    repository.upsert(LISTS_NOTE)
    repository.upsert(DICTS_NOTE)

    def _override_repo() -> NotesRepository:
        return repository

    app.dependency_overrides[notes_api.get_repository] = _override_repo
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_list_notes_endpoint(client: TestClient) -> None:
    response = client.get("/api/notes")
    assert response.status_code == 200
    body = response.json()
    assert [n["id"] for n in body] == ["lists", "dictionaries"]
    assert body[0]["title_fr"] is None


def test_get_note_endpoint(client: TestClient) -> None:
    response = client.get("/api/notes/dictionaries")
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Dictionaries"
    assert body["title_fr"] == "Dictionnaires"
    assert body["related_exercise_ids"] == ["piscine-00-sos"]


def test_get_missing_note_endpoint_returns_404(client: TestClient) -> None:
    response = client.get("/api/notes/does-not-exist")
    assert response.status_code == 404


def test_every_note_json_file_loads_and_seeds_without_error() -> None:
    json_files = sorted(NOTES_DIR.glob("*.json"))
    assert len(json_files) >= 4  # Lists, Dictionaries, Strings, Loops

    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repo = NotesRepository(connection)
    for path in json_files:
        note = load_note(path)
        assert note.id
        assert note.title
        assert note.related_exercise_ids, f"{note.id} has no related exercises"
        repo.upsert(note)
    connection.close()


def test_lists_and_dictionaries_notes_exist() -> None:
    ids = {load_note(p).id for p in NOTES_DIR.glob("*.json")}
    assert "lists" in ids
    assert "dictionaries" in ids


def test_related_exercise_ids_resolve_to_real_exercises() -> None:
    """Every id a note links to must exist, or the practice links 404."""
    from scripts.seed import EXERCISES_DIR
    from scripts.seed import load_exercise as load_exercise_json

    all_exercise_ids = {
        load_exercise_json(p).id for p in EXERCISES_DIR.glob("**/*.json")
    }
    for note_path in NOTES_DIR.glob("*.json"):
        note = load_note(note_path)
        for related_id in note.related_exercise_ids:
            assert related_id in all_exercise_ids, (
                f"{note.id} references missing exercise {related_id!r}"
            )
