"""Tests for the Sprint 3 bilingual (EN/FR) fields.

The backend never picks a locale server-side - it always returns both
the English field and its optional French sibling, and the frontend
falls back to English when the French one is null. These tests only
need to confirm the fields round-trip through storage and the API
correctly, including the "not translated yet" (null) case.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import exercises as exercises_api
from app.domain.models import Exercise, HiddenTest
from app.main import app
from app.models.database import SCHEMA
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService

TRANSLATED = Exercise(
    id="fr-001",
    module="m",
    difficulty=1,
    title="Hello",
    description="Say hello.",
    examples="e",
    starter_code="s",
    hints=["hint 1", "hint 2", "hint 3"],
    expected_behavior="b",
    hidden_tests=[HiddenTest(call="hello()", expected="'hi'")],
    solution="def hello():\n    return 'hi'\n",
    explanation="Just returns a literal.",
    concepts=[],
    title_fr="Bonjour",
    description_fr="Dis bonjour.",
    hints_fr=["indice 1", "indice 2", "indice 3"],
    explanation_fr="Retourne simplement un littéral.",
)

UNTRANSLATED = Exercise(
    id="fr-002",
    module="m",
    difficulty=1,
    title="Goodbye",
    description="Say goodbye.",
    examples="e",
    starter_code="s",
    hints=["only hint"],
    expected_behavior="b",
    hidden_tests=[],
    solution="def goodbye():\n    return 'bye'\n",
    explanation="Returns a literal.",
    concepts=[],
)


@pytest.fixture()
def i18n_conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def i18n_repo(i18n_conn: sqlite3.Connection) -> ExerciseRepository:
    repo = ExerciseRepository(i18n_conn)
    repo.upsert(TRANSLATED)
    repo.upsert(UNTRANSLATED)
    return repo


def test_french_fields_round_trip_through_storage(
    i18n_repo: ExerciseRepository,
) -> None:
    exercise = i18n_repo.get("fr-001")
    assert exercise.title_fr == "Bonjour"
    assert exercise.description_fr == "Dis bonjour."
    assert exercise.hints_fr == ["indice 1", "indice 2", "indice 3"]
    assert exercise.explanation_fr == "Retourne simplement un littéral."


def test_untranslated_exercise_has_null_french_fields(
    i18n_repo: ExerciseRepository,
) -> None:
    exercise = i18n_repo.get("fr-002")
    assert exercise.title_fr is None
    assert exercise.description_fr is None
    assert exercise.hints_fr is None
    assert exercise.explanation_fr is None


@pytest.fixture
def client() -> Iterator[TestClient]:
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = ExerciseRepository(connection)
    repository.upsert(TRANSLATED)
    repository.upsert(UNTRANSLATED)

    def _override_service() -> ExerciseService:
        return ExerciseService(repository)

    app.dependency_overrides[exercises_api.get_service] = _override_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_exercise_detail_exposes_french_fields(client: TestClient) -> None:
    response = client.get("/api/exercises/fr-001")
    assert response.status_code == 200
    body = response.json()
    assert body["title_fr"] == "Bonjour"
    assert body["description_fr"] == "Dis bonjour."


def test_exercise_detail_french_fields_are_null_when_untranslated(
    client: TestClient,
) -> None:
    response = client.get("/api/exercises/fr-002")
    assert response.status_code == 200
    body = response.json()
    assert body["title_fr"] is None
    assert body["description_fr"] is None


def test_hint_endpoint_returns_french_translation_when_available(
    client: TestClient,
) -> None:
    response = client.post("/api/exercises/fr-001/hint")
    assert response.status_code == 200
    body = response.json()
    assert body["hint"] == "hint 1"
    assert body["hint_fr"] == "indice 1"


def test_hint_endpoint_returns_null_french_when_untranslated(
    client: TestClient,
) -> None:
    response = client.post("/api/exercises/fr-002/hint")
    assert response.status_code == 200
    body = response.json()
    assert body["hint"] == "only hint"
    assert body["hint_fr"] is None


def test_solution_endpoint_returns_french_explanation_when_available(
    client: TestClient,
) -> None:
    response = client.post("/api/exercises/fr-001/solution")
    assert response.status_code == 200
    body = response.json()
    assert body["explanation_fr"] == "Retourne simplement un littéral."


def test_list_exercises_exposes_title_fr(client: TestClient) -> None:
    response = client.get("/api/exercises")
    assert response.status_code == 200
    by_id = {e["id"]: e for e in response.json()}
    assert by_id["fr-001"]["title_fr"] == "Bonjour"
    assert by_id["fr-002"]["title_fr"] is None
