"""Tests for the basic learning path (Sprint 3): prerequisite resolution
and the "next recommended exercise" endpoint. Deliberately simple, no
adaptive/scoring logic (see SPRINT_3_PLAN.md).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import exercises as exercises_api
from app.domain.models import Exercise, ExerciseStatus
from app.main import app
from app.models.database import SCHEMA
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService

EX_A = Exercise(
    id="ex-a",
    module="m",
    difficulty=1,
    title="Exercise A",
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

EX_B = Exercise(
    id="ex-b",
    module="m",
    difficulty=2,
    title="Exercise B",
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
    prerequisites=["ex-a", "ex-missing"],
)

EX_EXCLUDED = Exercise(
    id="ex-excluded",
    module="m",
    difficulty=1,
    title="Excluded",
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
    exercise_status="excluded",
)

EX_OTHER_SOURCE = Exercise(
    id="ex-other",
    module="m",
    difficulty=1,
    title="Other source",
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


@pytest.fixture()
def path_conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def path_repo(path_conn: sqlite3.Connection) -> ExerciseRepository:
    repo = ExerciseRepository(path_conn)
    for exercise in (EX_A, EX_B, EX_EXCLUDED, EX_OTHER_SOURCE):
        repo.upsert(exercise)
    return repo


def _mark_solved(repo: ExerciseRepository, exercise_id: str) -> None:
    progress = repo.get_progress(exercise_id)
    progress.status = ExerciseStatus.SOLVED
    repo.save_progress(progress)


def test_resolve_prerequisites_reports_unsolved_by_default(
    path_repo: ExerciseRepository,
) -> None:
    resolved = path_repo.resolve_prerequisites(EX_B.prerequisites)
    assert resolved == [
        {"id": "ex-a", "title": "Exercise A", "solved": False},
        {"id": "ex-missing", "title": "ex-missing", "solved": False},
    ]


def test_resolve_prerequisites_reflects_solved_state(
    path_repo: ExerciseRepository,
) -> None:
    _mark_solved(path_repo, "ex-a")
    resolved = path_repo.resolve_prerequisites(["ex-a"])
    assert resolved == [{"id": "ex-a", "title": "Exercise A", "solved": True}]


def test_resolve_prerequisites_of_empty_list_is_empty(
    path_repo: ExerciseRepository,
) -> None:
    assert path_repo.resolve_prerequisites([]) == []


def test_get_next_unsolved_returns_lowest_difficulty_first(
    path_repo: ExerciseRepository,
) -> None:
    next_exercise = path_repo.get_next_unsolved(source="python_gym")
    assert next_exercise is not None
    assert next_exercise.id == "ex-a"


def test_get_next_unsolved_advances_once_solved(
    path_repo: ExerciseRepository,
) -> None:
    _mark_solved(path_repo, "ex-a")
    next_exercise = path_repo.get_next_unsolved(source="python_gym")
    assert next_exercise is not None
    assert next_exercise.id == "ex-b"


def test_get_next_unsolved_returns_none_when_everything_solved(
    path_repo: ExerciseRepository,
) -> None:
    _mark_solved(path_repo, "ex-a")
    _mark_solved(path_repo, "ex-b")
    assert path_repo.get_next_unsolved(source="python_gym") is None


def test_get_next_unsolved_never_returns_excluded_exercises(
    path_repo: ExerciseRepository,
) -> None:
    for _ in range(5):
        result = path_repo.get_next_unsolved()
        assert result is None or result.id != "ex-excluded"


def test_get_next_unsolved_filters_by_source(path_repo: ExerciseRepository) -> None:
    result = path_repo.get_next_unsolved(source="foundations")
    assert result is not None
    assert result.id == "ex-other"


@pytest.fixture
def client() -> Iterator[TestClient]:
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = ExerciseRepository(connection)
    repository.upsert(EX_A)
    repository.upsert(EX_B)

    def _override_service() -> ExerciseService:
        return ExerciseService(repository)

    app.dependency_overrides[exercises_api.get_service] = _override_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_get_exercise_resolves_prerequisites_over_http(client: TestClient) -> None:
    response = client.get("/api/exercises/ex-b")
    assert response.status_code == 200
    body = response.json()
    assert body["prerequisites"] == [
        {"id": "ex-a", "title": "Exercise A", "solved": False},
        {"id": "ex-missing", "title": "ex-missing", "solved": False},
    ]


def test_next_endpoint_returns_lowest_difficulty_unsolved(
    client: TestClient,
) -> None:
    response = client.get("/api/exercises/next?source=python_gym")
    assert response.status_code == 200
    assert response.json()["id"] == "ex-a"


def test_next_endpoint_returns_null_when_nothing_left(client: TestClient) -> None:
    client.post("/api/exercises/ex-a/submit", json={"code": "x = 1"})
    client.post("/api/exercises/ex-b/submit", json={"code": "x = 1"})
    response = client.get("/api/exercises/next?source=does-not-exist")
    assert response.status_code == 200
    assert response.json() is None
