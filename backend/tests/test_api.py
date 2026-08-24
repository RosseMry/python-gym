"""End-to-end HTTP tests through FastAPI's TestClient.

The unit tests elsewhere in this suite exercise ExerciseService
directly. This file additionally checks that the HTTP routes wire
requests/responses correctly (status codes, JSON shape, 404s), using
dependency overrides so no real python_gym.db file is touched.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api import exercises as exercises_api
from app.api import progress as progress_api
from app.main import app
from app.models.database import SCHEMA
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService
from tests.conftest import SUM_EXERCISE


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A TestClient whose routes are backed by a seeded in-memory repo.

    TestClient dispatches requests on a worker thread, so this uses its
    own connection with ``check_same_thread=False`` rather than the
    shared ``conn``/``repo`` fixtures (whose in-memory connection is
    only valid on the thread that created it).
    """
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = ExerciseRepository(connection)
    repository.upsert(SUM_EXERCISE)

    def _override_service() -> ExerciseService:
        return ExerciseService(repository)

    app.dependency_overrides[exercises_api.get_service] = _override_service
    app.dependency_overrides[progress_api.get_service] = _override_service
    try:
        # Not using `with TestClient(app)` here: entering that context
        # triggers the startup event, which would call init_db() against
        # the real python_gym.db file. Routes don't need startup to run
        # since get_connection() is overridden away above.
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_exercises_returns_summaries_without_solution(
    client: TestClient,
) -> None:
    response = client.get("/api/exercises")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "loop-003"
    assert "solution" not in body[0]


def test_get_exercise_hides_solution_and_hidden_tests(client: TestClient) -> None:
    response = client.get("/api/exercises/loop-003")
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Sum the numbers"
    assert "solution" not in body
    assert "hidden_tests" not in body
    assert "hints" not in body


def test_get_missing_exercise_returns_404(client: TestClient) -> None:
    response = client.get("/api/exercises/does-not-exist")
    assert response.status_code == 404


def test_hint_endpoint_returns_hints_in_order(client: TestClient) -> None:
    first = client.post("/api/exercises/loop-003/hint")
    assert first.status_code == 200
    assert first.json() == {"hint": "hint 1", "hint_fr": None, "hint_function": None}

    second = client.post("/api/exercises/loop-003/hint")
    assert second.json() == {"hint": "hint 2", "hint_fr": None, "hint_function": None}


def test_submit_endpoint_reports_pass_fail(client: TestClient) -> None:
    correct = (
        "def sum_numbers(numbers):\n"
        "    total = 0\n"
        "    for number in numbers:\n"
        "        total += number\n"
        "    return total\n"
    )
    response = client.post(
        "/api/exercises/loop-003/submit", json={"code": correct}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["passed"] is True
    assert body["tests_passed"] == body["tests_total"] == 2


def test_submit_on_missing_exercise_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/exercises/does-not-exist/submit", json={"code": "x = 1"}
    )
    assert response.status_code == 404


def test_solution_endpoint_returns_solution_and_explanation(
    client: TestClient,
) -> None:
    response = client.post("/api/exercises/loop-003/solution")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body["solution"]
    assert body["explanation"] == "Accumulator pattern."


def test_explanation_endpoint_accepts_free_text(client: TestClient) -> None:
    response = client.post(
        "/api/exercises/loop-003/explanation",
        json={"text": "I loop and add each number to a running total."},
    )
    assert response.status_code == 204


def test_progress_endpoint_lists_records(client: TestClient) -> None:
    response = client.get("/api/progress")
    assert response.status_code == 200
    body = response.json()
    assert body[0]["exercise_id"] == "loop-003"
    assert body[0]["status"] == "NEW"


def test_repeated_source_filtered_requests_do_not_leak_connections(
    client: TestClient,
) -> None:
    """Regression test for Sprint 2's progressive_python reload 500s.

    get_service() used to open a fresh sqlite3 connection per request
    without ever closing it, so repeated requests (e.g. React
    StrictMode double-firing effects on every reload) accumulated open
    connections until one failed. 50 requests is comfortably past where
    the old code would start erroring.
    """
    for _ in range(50):
        response = client.get("/api/exercises?source=progressive_python")
        assert response.status_code == 200
