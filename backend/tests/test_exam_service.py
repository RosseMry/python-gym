"""Tests for the Timed Exam: session creation, timer, grading, timeout.

Covers both ExamService directly and the HTTP routes (spec section 2:
creation, timer, question selection, no hints, no solution reveal,
submission, score, result, timeout).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api import exam as exam_api
from app.domain.models import ExamQuestion, ExamSession, HiddenTest
from app.main import app
from app.models.database import SCHEMA
from app.repositories.exam_repository import ExamRepository
from app.services.exam_service import (
    ExamAlreadySubmittedError,
    ExamService,
    ExamSessionNotFoundError,
)

MCQ_QUESTION = ExamQuestion(
    id="q-mcq",
    kind="mcq",
    category="python_fundamentals",
    prompt="What is 2 + 2?",
    difficulty=1,
    points=1,
    choices=["3", "4", "5"],
    correct_choice=1,
    explanation="Basic arithmetic.",
)

OUTPUT_QUESTION = ExamQuestion(
    id="q-output",
    kind="output_prediction",
    category="python_fundamentals",
    prompt="print(1 + 1)",
    difficulty=1,
    points=1,
    expected_output="2",
    explanation="Basic arithmetic.",
)

CODING_QUESTION = ExamQuestion(
    id="q-coding",
    kind="coding",
    category="algorithms",
    prompt="Write add(a, b) that returns a + b.",
    difficulty=1,
    points=2,
    starter_code="def add(a, b):\n    pass\n",
    solution="def add(a, b):\n    return a + b\n",
    hidden_tests=[HiddenTest(call="add(2, 3)", expected="5")],
    explanation="Basic arithmetic.",
)


@pytest.fixture()
def repo() -> ExamRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repository = ExamRepository(connection)
    for q in (MCQ_QUESTION, OUTPUT_QUESTION, CODING_QUESTION):
        repository.upsert_question(q)
    return repository


@pytest.fixture()
def service(repo: ExamRepository) -> ExamService:
    return ExamService(repo)


def test_start_exam_creates_a_session_with_the_requested_question_count(
    service: ExamService,
) -> None:
    session, questions = service.start_exam(question_count=2, duration_seconds=600)
    assert len(questions) == 2
    assert session.question_ids == [q.id for q in questions]
    assert session.status == "in_progress"


def test_start_exam_caps_question_count_to_the_pool_size(
    service: ExamService,
) -> None:
    session, questions = service.start_exam(question_count=100, duration_seconds=600)
    assert len(questions) == 3  # only 3 questions exist in the fixture pool


def test_start_exam_with_empty_pool_raises() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    empty_service = ExamService(ExamRepository(connection))
    with pytest.raises(ValueError):
        empty_service.start_exam()


def test_deadline_is_computed_server_side_from_duration(
    service: ExamService,
) -> None:
    session, _ = service.start_exam(question_count=1, duration_seconds=300)
    started = datetime.fromisoformat(session.started_at)
    deadline = datetime.fromisoformat(session.deadline_at)
    assert (deadline - started).total_seconds() == 300


def test_get_session_round_trips(service: ExamService) -> None:
    session, questions = service.start_exam(question_count=2, duration_seconds=600)
    fetched_session, fetched_questions = service.get_session(session.id)
    assert fetched_session.id == session.id
    assert {q.id for q in fetched_questions} == {q.id for q in questions}


def test_get_session_unknown_id_raises(service: ExamService) -> None:
    with pytest.raises(ExamSessionNotFoundError):
        service.get_session("does-not-exist")


def test_submit_exam_grades_mcq_output_and_coding_correctly(
    service: ExamService,
) -> None:
    session, _ = service.start_exam(question_count=3, duration_seconds=600)
    answers = {
        "q-mcq": "1",
        "q-output": "2",
        "q-coding": "def add(a, b):\n    return a + b\n",
    }
    result = service.submit_exam(session.id, answers)
    assert result.status == "submitted"
    assert result.questions_correct == 3
    assert result.score == result.max_score == 4  # 1 + 1 + 2 points


def test_submit_exam_grades_wrong_answers_as_incorrect(
    service: ExamService,
) -> None:
    session, _ = service.start_exam(question_count=3, duration_seconds=600)
    answers = {
        "q-mcq": "0",
        "q-output": "wrong",
        "q-coding": "def add(a, b):\n    return 0\n",
    }
    result = service.submit_exam(session.id, answers)
    assert result.questions_correct == 0
    assert result.score == 0


def test_submit_exam_missing_answer_counts_as_incorrect(
    service: ExamService,
) -> None:
    session, _ = service.start_exam(question_count=3, duration_seconds=600)
    result = service.submit_exam(session.id, {})
    assert result.questions_correct == 0


def test_submit_exam_unknown_session_raises(service: ExamService) -> None:
    with pytest.raises(ExamSessionNotFoundError):
        service.submit_exam("does-not-exist", {})


def test_submit_exam_twice_raises(service: ExamService) -> None:
    session, _ = service.start_exam(question_count=1, duration_seconds=600)
    service.submit_exam(session.id, {})
    with pytest.raises(ExamAlreadySubmittedError):
        service.submit_exam(session.id, {})


def test_submit_after_deadline_is_marked_timed_out_but_still_graded(
    repo: ExamRepository, service: ExamService
) -> None:
    """A timed-out auto-submit is still evaluated (spec section 2's flow
    treats Submit and timeout as two paths into the same evaluation
    step), just recorded with status="timed_out" instead of "submitted".
    """
    past = datetime.now(timezone.utc) - timedelta(minutes=10)
    expired_session = ExamSession(
        id="expired-session",
        question_ids=["q-mcq"],
        started_at=(past - timedelta(minutes=5)).isoformat(),
        duration_seconds=300,
        deadline_at=past.isoformat(),
    )
    repo.create_session(expired_session)

    result = service.submit_exam("expired-session", {"q-mcq": "1"})
    assert result.status == "timed_out"
    assert result.questions_correct == 1  # still graded correctly


# --- HTTP-level tests (student-facing payload must never leak answers) ---


@pytest.fixture()
def client() -> Iterator[TestClient]:
    # TestClient dispatches on a worker thread, so this needs its own
    # check_same_thread=False connection rather than the shared `repo`
    # fixture's connection (see test_api.py's client fixture docstring).
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    http_repo = ExamRepository(connection)
    for q in (MCQ_QUESTION, OUTPUT_QUESTION, CODING_QUESTION):
        http_repo.upsert_question(q)

    def _override_service() -> ExamService:
        return ExamService(http_repo)

    app.dependency_overrides[exam_api.get_service] = _override_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_start_exam_endpoint_never_leaks_answers(client: TestClient) -> None:
    response = client.post("/api/exam/start")
    assert response.status_code == 200
    body = response.json()
    assert len(body["questions"]) == 3
    for q in body["questions"]:
        assert "correct_choice" not in q
        assert "expected_output" not in q
        assert "hidden_tests" not in q
        assert "solution" not in q
        assert "explanation" not in q


def test_submit_exam_endpoint_returns_score(client: TestClient) -> None:
    start_response = client.post("/api/exam/start")
    session_id = start_response.json()["session_id"]

    submit_response = client.post(
        f"/api/exam/{session_id}/submit",
        json={
            "answers": {
                "q-mcq": "1",
                "q-output": "2",
                "q-coding": "def add(a, b):\n    return a + b\n",
            }
        },
    )
    assert submit_response.status_code == 200
    body = submit_response.json()
    assert body["score"] == body["max_score"] == 4
    assert body["questions_correct"] == 3


def test_submit_exam_endpoint_twice_returns_409(client: TestClient) -> None:
    start_response = client.post("/api/exam/start")
    session_id = start_response.json()["session_id"]
    client.post(f"/api/exam/{session_id}/submit", json={"answers": {}})
    second = client.post(f"/api/exam/{session_id}/submit", json={"answers": {}})
    assert second.status_code == 409


def test_get_unknown_session_returns_404(client: TestClient) -> None:
    response = client.get("/api/exam/does-not-exist")
    assert response.status_code == 404
