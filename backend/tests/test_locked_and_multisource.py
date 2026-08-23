"""Tests for the Sprint 3 correction: locked exercises, day/level
metadata, and comma-separated multi-source filtering (the "Progressive
-> Foundations" merged nav link).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import exercises as exercises_api
from app.domain.models import Exercise
from app.main import app
from app.models.database import SCHEMA
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService

LOCKED_EXERCISE = Exercise(
    id="piscine-01-give-bmi",
    module="piscine_01_array",
    difficulty=2,
    title="Give BMI (locked)",
    description="Requires NumPy.",
    examples="",
    starter_code="",
    hints=[],
    expected_behavior="",
    hidden_tests=[],
    solution="",
    explanation="",
    concepts=["numpy"],
    source="42_python_piscine",
    exercise_status="locked",
)

ACTIVE_PISCINE = Exercise(
    id="piscine-00-hello",
    module="piscine_00_starting",
    difficulty=1,
    title="Hello",
    description="d",
    examples="e",
    starter_code="s",
    hints=[],
    expected_behavior="b",
    hidden_tests=[],
    solution="sol",
    explanation="exp",
    concepts=[],
    source="42_python_piscine",
)

FOUNDATIONS_EX = Exercise(
    id="fnd-x",
    module="variables",
    difficulty=1,
    title="Foundations exercise",
    description="d",
    examples="e",
    starter_code="s",
    hints=[],
    expected_behavior="b",
    hidden_tests=[],
    solution="sol",
    explanation="exp",
    concepts=[],
    source="foundations",
)

PYTHON_GYM_EX = Exercise(
    id="pg-x",
    module="strings",
    difficulty=1,
    title="Python-Gym exercise",
    description="d",
    examples="e",
    starter_code="s",
    hints=[],
    expected_behavior="b",
    hidden_tests=[],
    solution="sol",
    explanation="exp",
    concepts=[],
    source="python_gym",
)

THIRTY_DAYS_EX = Exercise(
    id="30days-d05-l1-01",
    module="lists",
    difficulty=1,
    title="Create an empty list",
    description="d",
    examples="e",
    starter_code="s",
    hints=[],
    expected_behavior="b",
    hidden_tests=[],
    solution="sol",
    explanation="exp",
    concepts=[],
    source="30_days_of_python",
    day=5,
    level=1,
)


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def repo(conn: sqlite3.Connection) -> ExerciseRepository:
    repository = ExerciseRepository(conn)
    for exercise in (
        LOCKED_EXERCISE,
        ACTIVE_PISCINE,
        FOUNDATIONS_EX,
        PYTHON_GYM_EX,
        THIRTY_DAYS_EX,
    ):
        repository.upsert(exercise)
    return repository


def test_day_and_level_round_trip(repo: ExerciseRepository) -> None:
    exercise = repo.get("30days-d05-l1-01")
    assert exercise.day == 5
    assert exercise.level == 1


def test_day_and_level_default_to_none(repo: ExerciseRepository) -> None:
    exercise = repo.get("fnd-x")
    assert exercise.day is None
    assert exercise.level is None


def test_locked_exercise_appears_in_list_by_source(repo: ExerciseRepository) -> None:
    results = repo.list_by_source("42_python_piscine")
    assert {e.id for e in results} == {"piscine-01-give-bmi", "piscine-00-hello"}


def test_locked_exercise_appears_in_list_all(repo: ExerciseRepository) -> None:
    results = repo.list_all()
    assert "piscine-01-give-bmi" in {e.id for e in results}


def test_locked_exercise_never_recommended_as_next(repo: ExerciseRepository) -> None:
    for _ in range(10):
        result = repo.get_next_unsolved(source="42_python_piscine")
        assert result is not None
        assert result.id != "piscine-01-give-bmi"


def test_comma_separated_source_merges_results(repo: ExerciseRepository) -> None:
    results = repo.list_by_source("foundations,progressive_python,python_gym")
    assert {e.id for e in results} == {"fnd-x", "pg-x"}


def test_comma_separated_source_excludes_unlisted_sources(
    repo: ExerciseRepository,
) -> None:
    results = repo.list_by_source("foundations,progressive_python,python_gym")
    assert "piscine-00-hello" not in {e.id for e in results}
    assert "30days-d05-l1-01" not in {e.id for e in results}


@pytest.fixture
def client() -> Iterator[TestClient]:
    # TestClient dispatches on a worker thread, so this needs its own
    # check_same_thread=False connection rather than the module-level
    # `conn`/`repo` fixtures (see test_api.py's client fixture).
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = ExerciseRepository(connection)
    for exercise in (
        LOCKED_EXERCISE,
        ACTIVE_PISCINE,
        FOUNDATIONS_EX,
        PYTHON_GYM_EX,
        THIRTY_DAYS_EX,
    ):
        repository.upsert(exercise)

    def _override_service() -> ExerciseService:
        return ExerciseService(repository)

    app.dependency_overrides[exercises_api.get_service] = _override_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_api_exposes_locked_status_day_and_level(client: TestClient) -> None:
    response = client.get("/api/exercises?source=42_python_piscine")
    assert response.status_code == 200
    by_id = {e["id"]: e for e in response.json()}
    assert by_id["piscine-01-give-bmi"]["exercise_status"] == "locked"
    assert by_id["piscine-00-hello"]["exercise_status"] == "active"

    day_response = client.get("/api/exercises?source=30_days_of_python")
    day_body = day_response.json()
    assert day_body[0]["day"] == 5
    assert day_body[0]["level"] == 1


def test_api_merges_multiple_sources(client: TestClient) -> None:
    response = client.get(
        "/api/exercises?source=foundations,progressive_python,python_gym"
    )
    assert response.status_code == 200
    ids = {e["id"] for e in response.json()}
    assert ids == {"fnd-x", "pg-x"}


def test_api_next_endpoint_skips_locked(client: TestClient) -> None:
    response = client.get("/api/exercises/next?source=42_python_piscine")
    assert response.status_code == 200
    body = response.json()
    assert body is not None
    assert body["id"] != "piscine-01-give-bmi"
