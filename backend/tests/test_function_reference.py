"""Tests for the Function Reference catalog (Sprint 3 finalization,
spec sections 6-7): reusable explanations a hint can link to instead of
duplicating the same content in every exercise.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import functions as functions_api
from app.domain.models import FunctionReference
from app.main import app
from app.models.database import SCHEMA
from app.repositories.function_reference_repository import (
    FunctionReferenceRepository,
)

ENUMERATE = FunctionReference(
    id="enumerate",
    name="enumerate()",
    what_it_does="Pairs each item with its index.",
    syntax="enumerate(iterable, start=0)",
    parameters="iterable, start",
    return_value="An enumerate object of (index, value) pairs.",
    example="for i, x in enumerate(['a', 'b']):\n    print(i, x)",
    example_output="0 a\n1 b",
    common_mistakes="Manually tracking an index instead of using this.",
    when_to_use="When a loop needs both the position and the value.",
    related_exercise_ids=["loop-009"],
    name_fr="enumerate()",
)

SUM_FN = FunctionReference(
    id="sum",
    name="sum()",
    what_it_does="Adds up the items of an iterable.",
    syntax="sum(iterable, start=0)",
    parameters="iterable, start",
    return_value="The total.",
    example="sum([1, 2, 3])",
    example_output="6",
    common_mistakes="Only works on numbers by default.",
    when_to_use="Totaling a list of numbers.",
)


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def repo(conn: sqlite3.Connection) -> FunctionReferenceRepository:
    repository = FunctionReferenceRepository(conn)
    repository.upsert(ENUMERATE)
    repository.upsert(SUM_FN)
    return repository


def test_list_all_orders_by_name(repo: FunctionReferenceRepository) -> None:
    functions = repo.list_all()
    assert [f.id for f in functions] == ["enumerate", "sum"]


def test_get_returns_full_detail(repo: FunctionReferenceRepository) -> None:
    function = repo.get("enumerate")
    assert function is not None
    assert function.syntax == "enumerate(iterable, start=0)"
    assert function.related_exercise_ids == ["loop-009"]
    assert function.name_fr == "enumerate()"


def test_get_missing_function_returns_none(repo: FunctionReferenceRepository) -> None:
    assert repo.get("does-not-exist") is None


def test_untranslated_function_has_null_french_fields(
    repo: FunctionReferenceRepository,
) -> None:
    function = repo.get("sum")
    assert function.name_fr is None
    assert function.what_it_does_fr is None


@pytest.fixture
def client() -> Iterator[TestClient]:
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = FunctionReferenceRepository(connection)
    repository.upsert(ENUMERATE)
    repository.upsert(SUM_FN)

    def _override_repo() -> FunctionReferenceRepository:
        return repository

    app.dependency_overrides[functions_api.get_repository] = _override_repo
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_list_functions_endpoint(client: TestClient) -> None:
    response = client.get("/api/functions")
    assert response.status_code == 200
    assert [f["id"] for f in response.json()] == ["enumerate", "sum"]


def test_get_function_endpoint(client: TestClient) -> None:
    response = client.get("/api/functions/enumerate")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "enumerate()"
    assert body["related_exercise_ids"] == ["loop-009"]


def test_get_missing_function_endpoint_returns_404(client: TestClient) -> None:
    response = client.get("/api/functions/does-not-exist")
    assert response.status_code == 404


def test_hint_endpoint_returns_linked_function_id() -> None:
    """An exercise's hint_functions[i] should flow through /hint as
    hint_function, so the frontend knows when to offer a "Learn: x()"
    link for that specific hint.
    """
    from app.api import exercises as exercises_api
    from app.domain.models import Exercise
    from app.repositories.exercise_repository import ExerciseRepository
    from app.services.exercise_service import ExerciseService

    exercise = Exercise(
        id="fn-ref-001",
        module="m",
        difficulty=1,
        title="t",
        description="d",
        examples="e",
        starter_code="s",
        hints=["hint 1", "hint 2"],
        expected_behavior="b",
        hidden_tests=[],
        solution="sol",
        explanation="exp",
        concepts=[],
        hint_functions=["sum", None],
    )
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = ExerciseRepository(connection)
    repository.upsert(exercise)

    def _override_service() -> ExerciseService:
        return ExerciseService(repository)

    app.dependency_overrides[exercises_api.get_service] = _override_service
    try:
        client = TestClient(app)
        first = client.post("/api/exercises/fn-ref-001/hint")
        assert first.json()["hint_function"] == "sum"
        second = client.post("/api/exercises/fn-ref-001/hint")
        assert second.json()["hint_function"] is None
    finally:
        app.dependency_overrides.clear()
        connection.close()
