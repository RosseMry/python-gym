"""Shared pytest fixtures: an isolated in-memory DB per test."""

from __future__ import annotations

import sqlite3

import pytest

from app.domain.models import Exercise, HiddenTest
from app.models.database import SCHEMA
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService

SUM_EXERCISE = Exercise(
    id="loop-003",
    module="for_loops",
    difficulty=2,
    title="Sum the numbers",
    description="Return the sum of a list of numbers using a loop.",
    examples="sum_numbers([1, 2, 3]) -> 6",
    starter_code="def sum_numbers(numbers):\n    pass\n",
    hints=["hint 1", "hint 2", "total = 0\nfor n in numbers:\n    total += n"],
    expected_behavior="Returns the sum.",
    hidden_tests=[
        HiddenTest(call="sum_numbers([1, 2, 3])", expected="6"),
        HiddenTest(call="sum_numbers([])", expected="0"),
    ],
    solution=(
        "def sum_numbers(numbers):\n"
        "    total = 0\n"
        "    for number in numbers:\n"
        "        total += number\n"
        "    return total\n"
    ),
    explanation="Accumulator pattern.",
    concepts=["for", "accumulator"],
)


@pytest.fixture()
def conn() -> sqlite3.Connection:
    """An isolated in-memory SQLite connection with the schema applied."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def repo(conn: sqlite3.Connection) -> ExerciseRepository:
    repository = ExerciseRepository(conn)
    repository.upsert(SUM_EXERCISE)
    return repository


@pytest.fixture()
def service(repo: ExerciseRepository) -> ExerciseService:
    return ExerciseService(repo)
