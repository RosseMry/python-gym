"""Regression tests for French content on the 42 Piscine catalog and
the 4 Learning Notes (Sprint 3 finalization, fourth correction). Also
covers the execution_service fix found while touching these files:
function-mode exercises with no hidden tests (piscine-00-loading,
piscine-00-package, and 7 others) used to always report "failed"
regardless of the submission - see test_execution_service.py's
test_function_mode_with_no_hidden_tests_reports_passed for the direct
regression test on that fix.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.domain.models import Exercise, LearningNote  # noqa: E402
from scripts.seed import EXERCISES_DIR, load_exercise  # noqa: E402
from scripts.seed_notes import NOTES_DIR, load_note  # noqa: E402


def _load_piscine() -> list[Exercise]:
    paths = sorted((EXERCISES_DIR / "42_python_piscine").glob("*.json"))
    return [load_exercise(p) for p in paths]


def _load_notes() -> list[LearningNote]:
    paths = sorted(NOTES_DIR.glob("*.json"))
    return [load_note(p) for p in paths]


_PISCINE = _load_piscine()
_PISCINE_IDS = [e.id for e in _PISCINE]
_NOTES = _load_notes()
_NOTE_IDS = [n.id for n in _NOTES]


def test_full_piscine_catalog_is_29_exercises() -> None:
    assert len(_PISCINE) == 29


def test_all_four_notes_are_present() -> None:
    assert {n.id for n in _NOTES} == {"lists", "dictionaries", "strings", "loops"}


@pytest.mark.parametrize("exercise", _PISCINE, ids=_PISCINE_IDS)
def test_every_piscine_exercise_has_french_content(exercise: Exercise) -> None:
    assert exercise.title_fr, exercise.id
    assert exercise.description_fr, exercise.id
    assert exercise.explanation_fr, exercise.id
    assert exercise.hints_fr, exercise.id
    assert len(exercise.hints_fr) == len(exercise.hints), exercise.id


@pytest.mark.parametrize("note", _NOTES, ids=_NOTE_IDS)
def test_every_note_has_french_content(note: LearningNote) -> None:
    assert note.title_fr, note.id
    assert note.explanation_fr, note.id
    assert note.syntax_fr, note.id
    assert note.examples_fr, note.id
    assert note.common_mistakes_fr, note.id
    assert note.mini_exercise_fr, note.id


@pytest.mark.parametrize("exercise", _PISCINE, ids=_PISCINE_IDS)
def test_no_piscine_hint_leaks_a_solution_line(exercise: Exercise) -> None:
    """Several Module 0/3/4 hints (written before the no-leak rule was
    established) had a hint 3 that was just the solution's code,
    verbatim - fixed as part of this pass. Guards against a repeat,
    in English and French.
    """
    solution_lines = {
        line.strip()
        for line in exercise.solution.splitlines()
        if len(line.strip()) > 20
        and not line.strip().startswith(
            ("import ", "def ", "from ", "class ", '"""', "@", "nonlocal ", "global ")
        )
    }
    for hint in exercise.hints:
        assert hint.strip() != exercise.solution.strip()
        for line in solution_lines:
            assert line not in hint, (exercise.id, "en", line, hint)
    if exercise.hints_fr:
        for hint_fr in exercise.hints_fr:
            for line in solution_lines:
                assert line not in hint_fr, (exercise.id, "fr", line, hint_fr)
