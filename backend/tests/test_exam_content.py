"""Tests for the exam question bank content under exam_questions/."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import ExamQuestion  # noqa: E402
from scripts.seed_exam import QUESTIONS_DIR, load_question  # noqa: E402

VALID_KINDS = {"mcq", "output_prediction", "debugging", "coding"}


@pytest.fixture(scope="module")
def questions() -> list[ExamQuestion]:
    paths = sorted(QUESTIONS_DIR.glob("*.json"))
    assert paths, f"no exam question files found under {QUESTIONS_DIR}"
    return [load_question(p) for p in paths]


def test_no_duplicate_ids(questions: list[ExamQuestion]) -> None:
    ids = [q.id for q in questions]
    assert len(ids) == len(set(ids))


def test_at_least_one_question_per_kind(questions: list[ExamQuestion]) -> None:
    kinds = {q.kind for q in questions}
    assert kinds == VALID_KINDS


def test_id_prefix_matches_kind_family(questions: list[ExamQuestion]) -> None:
    prefixes = {
        "mcq": "exam-mcq-",
        "coding": "exam-coding-",
        "output_prediction": "exam-output-",
        "debugging": "exam-debug-",
    }
    for q in questions:
        assert q.id.startswith(prefixes[q.kind]), q.id


def test_mcq_questions_have_valid_choices(questions: list[ExamQuestion]) -> None:
    for q in questions:
        if q.kind != "mcq":
            continue
        assert q.choices and len(q.choices) >= 2, q.id
        assert q.correct_choice is not None, q.id
        assert 0 <= q.correct_choice < len(q.choices), q.id


def test_output_and_debugging_questions_have_expected_output(
    questions: list[ExamQuestion],
) -> None:
    for q in questions:
        if q.kind in ("output_prediction", "debugging"):
            assert q.expected_output is not None and q.expected_output != "", q.id


def test_coding_questions_have_hidden_tests_and_a_passing_solution(
    questions: list[ExamQuestion],
) -> None:
    from app.domain.models import Exercise
    from app.services.execution_service import run_submission

    for q in questions:
        if q.kind != "coding":
            continue
        assert q.hidden_tests, q.id
        assert q.solution, q.id
        stand_in = Exercise(
            id=q.id,
            module="exam",
            difficulty=q.difficulty,
            title=q.prompt,
            description=q.prompt,
            examples="",
            starter_code=q.starter_code or "",
            hints=[],
            expected_behavior="",
            hidden_tests=q.hidden_tests,
            solution=q.solution,
            explanation=q.explanation,
        )
        result = run_submission(stand_in, q.solution)
        assert result.passed is True, (q.id, result.tests)


def test_every_question_has_explanation_and_positive_points(
    questions: list[ExamQuestion],
) -> None:
    for q in questions:
        assert q.explanation.strip(), q.id
        assert q.points >= 1, q.id
