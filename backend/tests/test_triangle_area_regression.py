"""Regression test for the reported triangle-area issue (Sprint 3
finalization spec section 9): a student could produce output that
superficially matched the example while using the wrong conversion
strategy, and the hints didn't teach the relevant concept (float() vs
int()) clearly enough. This locks in that the hints now actually teach
the concept, link to a real Function Reference entry, and never leak
the solution.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from scripts.seed import EXERCISES_DIR, load_exercise  # noqa: E402
from scripts.seed_functions import FUNCTIONS_DIR, load_function  # noqa: E402


@pytest.fixture()
def triangle_area_data() -> dict:
    path = EXERCISES_DIR / "30_days_of_python" / "30days-triangle-area.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_hints_teach_float_not_just_name_it(triangle_area_data: dict) -> None:
    hints = triangle_area_data["hints"]
    assert len(hints) == 3
    joined = " ".join(hints).lower()
    assert "float" in joined
    # The concept explanation must actually appear, not just the name.
    assert "decimal" in joined


def test_hints_explain_the_float_vs_int_distinction(triangle_area_data: dict) -> None:
    joined = " ".join(triangle_area_data["hints"]).lower()
    assert "int()" in joined or "int(" in joined


def test_no_hint_contains_the_complete_solution(triangle_area_data: dict) -> None:
    solution = triangle_area_data["solution"]
    for hint in triangle_area_data["hints"]:
        assert hint.strip() != solution.strip()
        # The full function definition must never appear inside a hint.
        assert "def main" not in hint


def test_hint_one_links_to_the_float_function_reference(
    triangle_area_data: dict,
) -> None:
    hint_functions = triangle_area_data.get("hint_functions")
    assert hint_functions is not None
    assert hint_functions[0] == "float"


def test_float_function_reference_exists_and_explains_int_difference() -> None:
    path = FUNCTIONS_DIR / "float.json"
    assert path.exists(), "functions/float.json must exist for the hint link to work"
    function = load_function(path)
    assert function.id == "float"
    assert "int()" in function.common_mistakes or "int()" in function.when_to_use


def test_triangle_area_solution_actually_uses_float() -> None:
    """The intended concept is float(), not int() dressed up to look right."""
    exercise = load_exercise(
        EXERCISES_DIR / "30_days_of_python" / "30days-triangle-area.json"
    )
    assert "float(" in exercise.solution
    # Word-boundary check - "print(" contains "int(" as a bare substring.
    assert re.search(r"\bint\(", exercise.solution) is None
