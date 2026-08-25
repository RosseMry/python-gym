"""HTTP-level tests for Mini Project grouping (SQL content reorganization).

Covers the two new, minimal endpoints added to app.api.sql: filtering
the exercise list by `project`, and listing distinct Mini Project ids -
the smallest surface needed for a frontend to render
"Mini Projects -> E-Commerce Sales Analysis -> Part 1/Part 2" without
a separate "project" table (see SqlExercise's docstring).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import sql as sql_api
from app.domain.models import SqlExercise, SqlHiddenTest
from app.main import app
from app.models.database import SCHEMA
from app.repositories.sql_exercise_repository import SqlExerciseRepository
from app.services.sql_exercise_service import SqlExerciseService


def _mini_project_exercise(exercise_id: str, part: int) -> SqlExercise:
    return SqlExercise(
        id=exercise_id,
        module="mini_project",
        difficulty=1,
        title="x",
        description="x",
        starter_query="-- your query here\n",
        hints=[],
        expected_behavior="x",
        hidden_tests=[SqlHiddenTest(expected=repr([]))],
        solution="SELECT 1;",
        explanation="x",
        concepts=[],
        schema="ecommerce_sales_analysis",
        project="ecommerce_sales_analysis",
        part=part,
    )


FOUNDATIONS_EXERCISE = SqlExercise(
    id="sql-foundations-01",
    module="foundations",
    difficulty=1,
    title="x",
    description="x",
    starter_query="-- your query here\n",
    hints=[],
    expected_behavior="x",
    hidden_tests=[SqlHiddenTest(expected=repr([]))],
    solution="SELECT 1;",
    explanation="x",
    concepts=[],
)


@pytest.fixture()
def repo() -> SqlExerciseRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = SqlExerciseRepository(connection)
    repository.upsert(FOUNDATIONS_EXERCISE)
    repository.upsert(_mini_project_exercise("sql-ecommerce-part1-01", part=1))
    repository.upsert(_mini_project_exercise("sql-ecommerce-part2-01", part=2))
    return repository


@pytest.fixture()
def client(repo: SqlExerciseRepository) -> Iterator[TestClient]:
    # TestClient dispatches on a worker thread, so this needs its own
    # check_same_thread=False connection (see test_api.py's client
    # fixture docstring for why the shared `repo` fixture can't be
    # reused directly here).
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    http_repo = SqlExerciseRepository(connection)
    http_repo.upsert(FOUNDATIONS_EXERCISE)
    http_repo.upsert(_mini_project_exercise("sql-ecommerce-part1-01", part=1))
    http_repo.upsert(_mini_project_exercise("sql-ecommerce-part2-01", part=2))

    def _override_service() -> SqlExerciseService:
        return SqlExerciseService(http_repo)

    app.dependency_overrides[sql_api.get_service] = _override_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_list_all_exercises_includes_mini_project_metadata(
    repo: SqlExerciseRepository,
) -> None:
    exercises = repo.list_all()
    by_id = {e.id: e for e in exercises}
    assert by_id["sql-ecommerce-part1-01"].project == "ecommerce_sales_analysis"
    assert by_id["sql-ecommerce-part1-01"].part == 1
    assert by_id["sql-foundations-01"].project is None


def test_project_filter_returns_only_that_project(
    repo: SqlExerciseRepository,
) -> None:
    exercises = repo.list_all(project="ecommerce_sales_analysis")
    assert {e.id for e in exercises} == {
        "sql-ecommerce-part1-01",
        "sql-ecommerce-part2-01",
    }


def test_project_filter_orders_by_part(repo: SqlExerciseRepository) -> None:
    # part2 upserted after part1, but the query must order by part.
    exercises = repo.list_all(project="ecommerce_sales_analysis")
    assert [e.part for e in exercises] == [1, 2]


def test_list_projects_returns_distinct_project_ids(
    repo: SqlExerciseRepository,
) -> None:
    assert repo.list_projects() == ["ecommerce_sales_analysis"]


def test_list_exercises_endpoint_filters_by_project(client: TestClient) -> None:
    response = client.get(
        "/api/sql/exercises", params={"project": "ecommerce_sales_analysis"}
    )
    assert response.status_code == 200
    body = response.json()
    assert {item["id"] for item in body} == {
        "sql-ecommerce-part1-01",
        "sql-ecommerce-part2-01",
    }
    assert all(item["project"] == "ecommerce_sales_analysis" for item in body)


def test_list_projects_endpoint(client: TestClient) -> None:
    response = client.get("/api/sql/exercises/projects/list")
    assert response.status_code == 200
    assert response.json() == ["ecommerce_sales_analysis"]


def test_exercise_detail_endpoint_includes_project_and_part(
    client: TestClient,
) -> None:
    response = client.get("/api/sql/exercises/sql-ecommerce-part1-01")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "ecommerce_sales_analysis"
    assert body["part"] == 1
