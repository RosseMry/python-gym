"""Tests for the seed mechanism loading all Sprint 2 content sources.

Spec section 39 - new content must load through the existing seed
mechanism, and spec section 38 explicitly calls out "seed loading" as
something that needs test coverage.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.models.database import SCHEMA  # noqa: E402
from app.repositories.exercise_repository import ExerciseRepository  # noqa: E402
from scripts.seed import EXERCISES_DIR, load_exercise  # noqa: E402

EXPECTED_SOURCES = {
    "progressive_python",
    "42_python_piscine",
    "30_days_of_python",
    "foundations",
    "python_gym",
}


@pytest.fixture()
def seeded_repo() -> ExerciseRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    repo = ExerciseRepository(connection)
    for path in sorted(EXERCISES_DIR.glob("**/*.json")):
        repo.upsert(load_exercise(path))
    yield repo
    connection.close()


def test_every_json_file_loads_without_error() -> None:
    json_files = sorted(EXERCISES_DIR.glob("**/*.json"))
    assert len(json_files) > 0
    for path in json_files:
        exercise = load_exercise(path)
        assert exercise.id
        assert exercise.title


def test_all_expected_sources_are_present(seeded_repo: ExerciseRepository) -> None:
    all_exercises = seeded_repo.list_all(include_excluded=True)
    sources = {e.source for e in all_exercises}
    assert EXPECTED_SOURCES.issubset(sources)


def test_42_piscine_exercises_use_the_42_validation_profile(
    seeded_repo: ExerciseRepository,
) -> None:
    piscine_exercises = seeded_repo.list_by_source("42_python_piscine")
    assert len(piscine_exercises) > 0
    assert all(e.validation_profile == "42_piscine" for e in piscine_exercises)


def test_script_mode_exercises_have_no_call_hidden_tests(
    seeded_repo: ExerciseRepository,
) -> None:
    """Script-mode exercises' hidden tests (if any) must use args, not call."""
    for exercise in seeded_repo.list_all(include_excluded=True):
        if exercise.exercise_type != "script":
            continue
        for test in exercise.hidden_tests:
            assert test.is_script_mode, (
                f"{exercise.id} is script-mode but has a call-mode hidden test"
            )


def test_ids_are_unique_across_all_sources() -> None:
    json_files = sorted(EXERCISES_DIR.glob("**/*.json"))
    ids = [load_exercise(path).id for path in json_files]
    assert len(ids) == len(set(ids))


def test_catalog_was_substantially_expanded_in_sprint_3(
    seeded_repo: ExerciseRepository,
) -> None:
    """Sprint 3 added 46 exercises (43 -> 89) - guard against silently
    losing content in a future refactor of the exercises/ layout.
    """
    all_exercises = seeded_repo.list_all(include_excluded=True)
    assert len(all_exercises) >= 168

    by_source: dict[str, int] = {}
    for exercise in all_exercises:
        by_source[exercise.source] = by_source.get(exercise.source, 0) + 1
    assert by_source.get("foundations", 0) >= 8
    # The Sprint 3 correction recategorized 6 invented "30-days-inspired"
    # exercises to python_gym, so the floor here rises accordingly.
    assert by_source.get("python_gym", 0) >= 32
    assert by_source.get("progressive_python", 0) >= 28
    # Every day 1-23 has real content now; days 24-30 are legitimately
    # absent (need a NumPy/Pandas track, a running web server/database,
    # or don't exist in the source at all - see gen_day*.py docstrings
    # and the test_days_*_are_imported tests for the per-day breakdown).
    assert by_source.get("30_days_of_python", 0) >= 244
    # Full 29-exercise Piscine catalog (19 Module 0/3/4 + 10 Module 1/2,
    # Sprint 3 finalization: Module 1 (Array/NumPy) and Module 2
    # (DataTable/pandas) are no longer locked placeholders - they now
    # ship real, gradable content, see
    # test_piscine_module1_and_module2_are_active_and_gradable.
    assert by_source.get("42_python_piscine", 0) == 29


def test_days_5_to_8_are_completely_imported(seeded_repo: ExerciseRepository) -> None:
    """Regression guard for the real per-day exercise counts fetched
    from the source repo (not estimated) - Day 5 Lists 31 (27 Level 1
    + 4 Level 2, the source has 4 not 3), Day 6 Tuples 12 (5+7), Day 7
    Sets 15 (5+7+3), Day 8 Dictionaries 11 (flat, no levels).
    """
    thirty_days = seeded_repo.list_by_source("30_days_of_python")
    by_day: dict[int, int] = {}
    for exercise in thirty_days:
        if exercise.day is not None:
            by_day[exercise.day] = by_day.get(exercise.day, 0) + 1
    assert by_day.get(5) == 31
    assert by_day.get(6) == 12
    assert by_day.get(7) == 15
    assert by_day.get(8) == 11


def test_days_2_4_10_18_19_are_imported(seeded_repo: ExerciseRepository) -> None:
    """Regression guard for the 5 days added in the second Sprint 3
    finalization correction (spec section 2). Counts are produced
    exercises, not raw source-item counts - several source items were
    consolidated or split with disclosure (see gen_day02.py's docstring
    for the heaviest case, Day 2's non-gradable "declare a variable
    with your own name" items).
    """
    thirty_days = seeded_repo.list_by_source("30_days_of_python")
    by_day: dict[int, int] = {}
    for exercise in thirty_days:
        if exercise.day is not None:
            by_day[exercise.day] = by_day.get(exercise.day, 0) + 1
    assert by_day.get(2) == 8
    assert by_day.get(4) == 25
    assert by_day.get(10) == 14
    assert by_day.get(18) == 4
    assert by_day.get(19) == 8


def test_days_3_11_14_20_21_are_imported(seeded_repo: ExerciseRepository) -> None:
    """Regression guard for the 5 days added in the third Sprint 3
    finalization correction (spec section 2). Day 3's 2 pre-existing
    exercises are now tagged day=3 (they used to have no day/level at
    all, making them invisible on the one-page view). Days 11 and 14
    already had Level 1 imported; this added their remaining levels.
    Day 20's remaining items need live network access to third-party
    APIs that are now dead or auth-gated (checked directly, not
    assumed) and are mostly represented as cross-references to
    existing exercises rather than duplicated - see gen_day20.py's
    docstring.
    """
    thirty_days = seeded_repo.list_by_source("30_days_of_python")
    by_day: dict[int, int] = {}
    for exercise in thirty_days:
        if exercise.day is not None:
            by_day[exercise.day] = by_day.get(exercise.day, 0) + 1
    assert by_day.get(3) == 20
    assert by_day.get(11) == 25
    assert by_day.get(14) == 20
    assert by_day.get(20) == 3
    assert by_day.get(21) == 2


def test_piscine_module1_and_module2_are_active_and_gradable(
    seeded_repo: ExerciseRepository,
) -> None:
    """Module 1 (Array/NumPy) + Module 2 (DataTable/pandas) shipped real
    content in the Sprint 3 finalization correction - no longer locked
    placeholders, each has real starter code and at least one hidden
    test that can actually grade a submission.
    """
    piscine = seeded_repo.list_all(module=None, include_excluded=True)
    module1_2 = [
        e
        for e in piscine
        if e.source == "42_python_piscine"
        and e.module in {"piscine_01_array", "piscine_02_datatable"}
    ]
    assert len(module1_2) == 10
    for exercise in module1_2:
        assert exercise.exercise_status == "active", exercise.id
        assert exercise.starter_code.strip(), exercise.id
        assert exercise.hidden_tests, exercise.id
