"""Tests for validation_profile driving optional style checks (section 29-32)."""

from __future__ import annotations

from app.services.exercise_service import ExerciseService


def test_standard_profile_never_runs_style_check(service: ExerciseService) -> None:
    """loop-003 (fixture) uses the default standard_python profile."""
    result = service.submit(
        "loop-003",
        "def sum_numbers(numbers):\n    total=0\n    for n in numbers:total+=n\n"
        "    return total\n",
    )
    assert result.style is None


def test_42_piscine_profile_runs_style_check(script_service) -> None:
    result = script_service.submit(
        "script-001", "import sys\nprint(sys.argv[1])\n"
    )
    assert result.style is not None
    assert result.style.ran is True


def test_style_failure_does_not_change_test_pass_status(script_service) -> None:
    # Badly formatted but functionally correct code should still pass
    # the hidden tests; style is reported separately (spec section 32).
    badly_formatted = "import sys\nprint( sys.argv[1] )\n"
    result = script_service.submit("script-001", badly_formatted)
    assert result.passed is True
    assert result.style is not None
