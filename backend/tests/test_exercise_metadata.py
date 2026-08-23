"""Tests for Sprint 2 exercise metadata (spec sections 17-21, 26, 33)."""

from __future__ import annotations

import sqlite3

import pytest

from app.domain.models import Exercise, HiddenTest
from app.models.database import SCHEMA
from app.repositories.exercise_repository import ExerciseRepository
from app.services.exercise_service import ExerciseService

PISCINE_EXERCISE = Exercise(
    id="piscine-001",
    module="basics",
    difficulty=1,
    title="First python script",
    description="Modify the strings.",
    examples="ex",
    starter_code="ft_list = []\n",
    hints=["hint"],
    expected_behavior="Prints the greetings.",
    hidden_tests=[HiddenTest(args=[], expected_stdout="Hello World!", label="Test 1")],
    solution="print('Hello World!')\n",
    explanation="Prints a literal.",
    concepts=["strings"],
    skills=["basic_syntax"],
    prerequisites=[],
    resources=[],
    source="42_python_piscine",
    track="python",
    validation_profile="42_piscine",
    exercise_type="script",
)

EXCLUDED_EXERCISE = Exercise(
    id="piscine-compression",
    module="excluded",
    difficulty=3,
    title="Compression (excluded)",
    description="Excluded per Sprint 2 spec section 33.",
    examples="",
    starter_code="",
    hints=[],
    expected_behavior="",
    hidden_tests=[],
    solution="",
    explanation="",
    concepts=[],
    source="42_python_piscine",
    exercise_status="excluded",
)


@pytest.fixture()
def piscine_conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    yield connection
    connection.close()


@pytest.fixture()
def piscine_repo(piscine_conn: sqlite3.Connection) -> ExerciseRepository:
    repo = ExerciseRepository(piscine_conn)
    repo.upsert(PISCINE_EXERCISE)
    repo.upsert(EXCLUDED_EXERCISE)
    return repo


def test_metadata_round_trips_through_storage(
    piscine_repo: ExerciseRepository,
) -> None:
    exercise = piscine_repo.get("piscine-001")
    assert exercise is not None
    assert exercise.source == "42_python_piscine"
    assert exercise.track == "python"
    assert exercise.skills == ["basic_syntax"]
    assert exercise.validation_profile == "42_piscine"
    assert exercise.exercise_type == "script"


def test_default_metadata_for_sprint1_style_exercise(
    piscine_repo: ExerciseRepository,
) -> None:
    plain = Exercise(
        id="plain-001",
        module="conditions",
        difficulty=1,
        title="plain",
        description="d",
        examples="e",
        starter_code="s",
        hints=[],
        expected_behavior="b",
        hidden_tests=[],
        solution="sol",
        explanation="exp",
        concepts=[],
    )
    piscine_repo.upsert(plain)
    reloaded = piscine_repo.get("plain-001")
    assert reloaded.source == "progressive_python"
    assert reloaded.track == "python"
    assert reloaded.validation_profile == "standard_python"
    assert reloaded.exercise_type == "function"


def test_list_by_source_filters_correctly(piscine_repo: ExerciseRepository) -> None:
    service = ExerciseService(piscine_repo)
    results = service.list_by_source("42_python_piscine")
    # The excluded exercise must never show up, even filtered by source.
    assert [e.id for e in results] == ["piscine-001"]


def test_excluded_exercise_is_hidden_from_list_all(
    piscine_repo: ExerciseRepository,
) -> None:
    all_active = piscine_repo.list_all()
    assert "piscine-compression" not in [e.id for e in all_active]


def test_excluded_exercise_can_still_be_fetched_directly(
    piscine_repo: ExerciseRepository,
) -> None:
    # Fetching by id is unaffected - only listings hide excluded items,
    # so a stale bookmark doesn't 404 (spec section 33 talks about
    # learning-path visibility, not deletion).
    exercise = piscine_repo.get("piscine-compression")
    assert exercise is not None
    assert exercise.exercise_status == "excluded"


def test_include_excluded_flag_surfaces_it_when_asked(
    piscine_repo: ExerciseRepository,
) -> None:
    everything = piscine_repo.list_all(include_excluded=True)
    assert "piscine-compression" in [e.id for e in everything]
