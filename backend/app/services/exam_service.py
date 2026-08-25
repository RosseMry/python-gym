"""Business logic for the Timed Exam (spec section 2).

One compact feature internally covering several question kinds (mcq,
output prediction, debugging, coding) - never separate sidebar
entries. Coding questions are graded by reusing execution_service's
existing Python sandbox directly, not a parallel grading path.
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone

from app.domain.models import (
    Exercise,
    ExamAnswerResult,
    ExamQuestion,
    ExamResult,
    ExamSession,
)
from app.repositories.exam_repository import ExamRepository
from app.services.execution_service import run_submission

DEFAULT_QUESTION_COUNT = 8
DEFAULT_DURATION_SECONDS = 20 * 60


class ExamSessionNotFoundError(Exception):
    """Raised when an exam session id does not exist."""


class ExamAlreadySubmittedError(Exception):
    """Raised when submitting a session that was already graded."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ExamService:
    """Creates timed exam sessions and grades submissions."""

    def __init__(self, repository: ExamRepository) -> None:
        self._repo = repository

    def start_exam(
        self,
        question_count: int = DEFAULT_QUESTION_COUNT,
        duration_seconds: int = DEFAULT_DURATION_SECONDS,
    ) -> tuple[ExamSession, list[ExamQuestion]]:
        """Pick a question set and open a server-timed session.

        The deadline is computed here, once, and stored - the client
        only ever displays a countdown to it, never supplies or
        extends it (spec section 2).
        """
        pool = self._repo.list_questions()
        if not pool:
            raise ValueError("No exam questions are seeded yet.")
        chosen = random.sample(pool, k=min(question_count, len(pool)))

        started_at = datetime.now(timezone.utc)
        deadline_at = started_at + timedelta(seconds=duration_seconds)
        session = ExamSession(
            id=str(uuid.uuid4()),
            question_ids=[q.id for q in chosen],
            started_at=started_at.isoformat(),
            duration_seconds=duration_seconds,
            deadline_at=deadline_at.isoformat(),
        )
        self._repo.create_session(session)
        return session, chosen

    def get_session(self, session_id: str) -> tuple[ExamSession, list[ExamQuestion]]:
        session = self._repo.get_session(session_id)
        if session is None:
            raise ExamSessionNotFoundError(session_id)
        questions = [
            q
            for qid in session.question_ids
            if (q := self._repo.get_question(qid)) is not None
        ]
        return session, questions

    def submit_exam(self, session_id: str, answers: dict[str, str]) -> ExamResult:
        """Grade every question and store the final result.

        Accepts a submission whether it arrives before or after the
        deadline (a timed-out auto-submit is still evaluated, just
        marked "timed_out" instead of "submitted") - spec section 2's
        flow treats "Submit" and "timeout" as two paths into the same
        evaluation step, not a rejection.
        """
        session = self._repo.get_session(session_id)
        if session is None:
            raise ExamSessionNotFoundError(session_id)
        if session.status != "in_progress":
            raise ExamAlreadySubmittedError(session_id)

        now = datetime.now(timezone.utc)
        deadline = datetime.fromisoformat(session.deadline_at)
        timed_out = now > deadline

        breakdown: list[ExamAnswerResult] = []
        total_score = 0
        max_score = 0
        for question_id in session.question_ids:
            question = self._repo.get_question(question_id)
            if question is None:
                continue
            max_score += question.points
            answer = answers.get(question_id, "")
            correct = self._grade_answer(question, answer)
            earned = question.points if correct else 0
            total_score += earned
            breakdown.append(
                ExamAnswerResult(
                    question_id=question_id,
                    correct=correct,
                    points_earned=earned,
                    points_possible=question.points,
                )
            )

        updated = ExamSession(
            id=session.id,
            question_ids=session.question_ids,
            started_at=session.started_at,
            duration_seconds=session.duration_seconds,
            deadline_at=session.deadline_at,
            status="timed_out" if timed_out else "submitted",
            answers=answers,
            submitted_at=_now_iso(),
            score=total_score,
            max_score=max_score,
        )
        self._repo.save_session(updated)

        started_at = datetime.fromisoformat(session.started_at)
        time_used = int((now - started_at).total_seconds())
        return ExamResult(
            session_id=session.id,
            status=updated.status,
            score=total_score,
            max_score=max_score,
            questions_total=len(breakdown),
            questions_correct=sum(1 for b in breakdown if b.correct),
            time_used_seconds=min(time_used, session.duration_seconds),
            answers=breakdown,
        )

    def _grade_answer(self, question: ExamQuestion, answer: str) -> bool:
        if question.kind == "mcq":
            try:
                return int(answer) == question.correct_choice
            except ValueError:
                return False
        if question.kind in ("output_prediction", "debugging"):
            expected = (question.expected_output or "").strip()
            return answer.strip() == expected
        if question.kind == "coding":
            return self._grade_coding_answer(question, answer)
        return False

    def _grade_coding_answer(self, question: ExamQuestion, answer: str) -> bool:
        if not question.hidden_tests:
            return False
        stand_in_exercise = Exercise(
            id=question.id,
            module="exam",
            difficulty=question.difficulty,
            title=question.prompt,
            description=question.prompt,
            examples="",
            starter_code=question.starter_code or "",
            hints=[],
            expected_behavior="",
            hidden_tests=question.hidden_tests,
            solution=question.solution or "",
            explanation=question.explanation,
        )
        result = run_submission(stand_in_exercise, answer)
        return result.passed
