"""Data access layer for the exam question bank and sessions (Sprint 4)."""

from __future__ import annotations

import json
import sqlite3

from app.domain.models import ExamQuestion, ExamSession, HiddenTest


def _row_to_question(row: sqlite3.Row) -> ExamQuestion:
    return ExamQuestion(
        id=row["id"],
        kind=row["kind"],
        category=row["category"],
        prompt=row["prompt"],
        difficulty=row["difficulty"],
        points=row["points"],
        code_snippet=row["code_snippet"],
        starter_code=row["starter_code"],
        choices=json.loads(row["choices"]) if row["choices"] else None,
        correct_choice=row["correct_choice"],
        expected_output=row["expected_output"],
        hidden_tests=(
            [HiddenTest(**t) for t in json.loads(row["hidden_tests"])]
            if row["hidden_tests"]
            else None
        ),
        solution=row["solution"],
        explanation=row["explanation"],
        source=row["source"],
    )


def _row_to_session(row: sqlite3.Row) -> ExamSession:
    return ExamSession(
        id=row["id"],
        question_ids=json.loads(row["question_ids"]),
        started_at=row["started_at"],
        duration_seconds=row["duration_seconds"],
        deadline_at=row["deadline_at"],
        status=row["status"],
        answers=json.loads(row["answers"]),
        submitted_at=row["submitted_at"],
        score=row["score"],
        max_score=row["max_score"],
    )


class ExamRepository:
    """Reads and writes exam questions and exam sessions."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert_question(self, question: ExamQuestion) -> None:
        """Insert or replace one exam question (used by the seed script)."""
        self._conn.execute(
            """
            INSERT INTO exam_questions (
                id, kind, category, prompt, difficulty, points,
                code_snippet, starter_code, choices, correct_choice,
                expected_output, hidden_tests, solution, explanation, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                kind=excluded.kind,
                category=excluded.category,
                prompt=excluded.prompt,
                difficulty=excluded.difficulty,
                points=excluded.points,
                code_snippet=excluded.code_snippet,
                starter_code=excluded.starter_code,
                choices=excluded.choices,
                correct_choice=excluded.correct_choice,
                expected_output=excluded.expected_output,
                hidden_tests=excluded.hidden_tests,
                solution=excluded.solution,
                explanation=excluded.explanation,
                source=excluded.source
            """,
            (
                question.id,
                question.kind,
                question.category,
                question.prompt,
                question.difficulty,
                question.points,
                question.code_snippet,
                question.starter_code,
                json.dumps(question.choices) if question.choices else None,
                question.correct_choice,
                question.expected_output,
                (
                    json.dumps([t.__dict__ for t in question.hidden_tests])
                    if question.hidden_tests
                    else None
                ),
                question.solution,
                question.explanation,
                question.source,
            ),
        )
        self._conn.commit()

    def get_question(self, question_id: str) -> ExamQuestion | None:
        row = self._conn.execute(
            "SELECT * FROM exam_questions WHERE id = ?", (question_id,)
        ).fetchone()
        return _row_to_question(row) if row else None

    def list_questions(self) -> list[ExamQuestion]:
        rows = self._conn.execute("SELECT * FROM exam_questions ORDER BY id").fetchall()
        return [_row_to_question(r) for r in rows]

    def create_session(self, session: ExamSession) -> None:
        self._conn.execute(
            """
            INSERT INTO exam_sessions (
                id, question_ids, started_at, duration_seconds,
                deadline_at, status, answers, submitted_at, score, max_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.id,
                json.dumps(session.question_ids),
                session.started_at,
                session.duration_seconds,
                session.deadline_at,
                session.status,
                json.dumps(session.answers),
                session.submitted_at,
                session.score,
                session.max_score,
            ),
        )
        self._conn.commit()

    def get_session(self, session_id: str) -> ExamSession | None:
        row = self._conn.execute(
            "SELECT * FROM exam_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        return _row_to_session(row) if row else None

    def save_session(self, session: ExamSession) -> None:
        self._conn.execute(
            """
            UPDATE exam_sessions SET
                status = ?, answers = ?, submitted_at = ?, score = ?, max_score = ?
            WHERE id = ?
            """,
            (
                session.status,
                json.dumps(session.answers),
                session.submitted_at,
                session.score,
                session.max_score,
                session.id,
            ),
        )
        self._conn.commit()
