"""HTTP routes for the Timed Exam (spec section 2).

One compact feature - "Start Exam" and "Submit" are the only two
actions a client needs. Question kind/category are internal grading
details, never separate routes or navigation items.
"""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.database import get_connection
from app.repositories.exam_repository import ExamRepository
from app.services.exam_service import (
    ExamAlreadySubmittedError,
    ExamSessionNotFoundError,
    ExamService,
)

router = APIRouter(prefix="/api/exam", tags=["exam"])


def get_service() -> Iterator[ExamService]:
    """Build a service instance with a fresh DB connection per request."""
    conn = get_connection()
    try:
        yield ExamService(ExamRepository(conn))
    finally:
        conn.close()


class ExamQuestionForStudent(BaseModel):
    """A question with every answer-revealing field stripped out."""

    id: str
    kind: str
    category: str
    prompt: str
    points: int
    code_snippet: str | None
    starter_code: str | None
    choices: list[str] | None


class ExamSessionResponse(BaseModel):
    session_id: str
    started_at: str
    duration_seconds: int
    deadline_at: str
    status: str
    questions: list[ExamQuestionForStudent]


class ExamSubmitRequest(BaseModel):
    answers: dict[str, str]


class ExamAnswerResultResponse(BaseModel):
    question_id: str
    correct: bool
    points_earned: int
    points_possible: int


class ExamResultResponse(BaseModel):
    session_id: str
    status: str
    score: float
    max_score: float
    questions_total: int
    questions_correct: int
    time_used_seconds: int
    answers: list[ExamAnswerResultResponse]


def _to_student_question(question) -> ExamQuestionForStudent:
    return ExamQuestionForStudent(
        id=question.id,
        kind=question.kind,
        category=question.category,
        prompt=question.prompt,
        points=question.points,
        code_snippet=question.code_snippet,
        starter_code=question.starter_code,
        choices=question.choices,
    )


@router.post("/start", response_model=ExamSessionResponse)
def start_exam(service: ExamService = Depends(get_service)) -> ExamSessionResponse:
    """Start a new timed exam session (spec section 2's flow entry point)."""
    try:
        session, questions = service.start_exam()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ExamSessionResponse(
        session_id=session.id,
        started_at=session.started_at,
        duration_seconds=session.duration_seconds,
        deadline_at=session.deadline_at,
        status=session.status,
        questions=[_to_student_question(q) for q in questions],
    )


@router.get("/{session_id}", response_model=ExamSessionResponse)
def get_exam_session(
    session_id: str, service: ExamService = Depends(get_service)
) -> ExamSessionResponse:
    """Return the current session state (for reloading an in-progress exam)."""
    try:
        session, questions = service.get_session(session_id)
    except ExamSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exam session not found") from exc
    return ExamSessionResponse(
        session_id=session.id,
        started_at=session.started_at,
        duration_seconds=session.duration_seconds,
        deadline_at=session.deadline_at,
        status=session.status,
        questions=[_to_student_question(q) for q in questions],
    )


@router.post("/{session_id}/submit", response_model=ExamResultResponse)
def submit_exam(
    session_id: str,
    body: ExamSubmitRequest,
    service: ExamService = Depends(get_service),
) -> ExamResultResponse:
    """Grade the exam (submit or a timed-out auto-submit both land here)."""
    try:
        result = service.submit_exam(session_id, body.answers)
    except ExamSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Exam session not found") from exc
    except ExamAlreadySubmittedError as exc:
        raise HTTPException(
            status_code=409, detail="This exam session was already submitted"
        ) from exc
    return ExamResultResponse(
        session_id=result.session_id,
        status=result.status,
        score=result.score,
        max_score=result.max_score,
        questions_total=result.questions_total,
        questions_correct=result.questions_correct,
        time_used_seconds=result.time_used_seconds,
        answers=[
            ExamAnswerResultResponse(
                question_id=a.question_id,
                correct=a.correct,
                points_earned=a.points_earned,
                points_possible=a.points_possible,
            )
            for a in result.answers
        ],
    )
