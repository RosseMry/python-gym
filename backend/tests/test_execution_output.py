"""Tests for Sprint 2 execution feedback: stdout separation, script mode.

Spec sections 10-15: the student must see their own program's output,
separate from stderr and from hidden-test internals.
"""

from __future__ import annotations

from app.domain.models import Exercise, HiddenTest
from app.services.execution_service import run_submission

FUNCTION_EXERCISE = Exercise(
    id="x",
    module="for_loops",
    difficulty=1,
    title="x",
    description="x",
    examples="x",
    starter_code="x",
    hints=[],
    expected_behavior="x",
    hidden_tests=[HiddenTest(call="print_all([1, 2])", expected="None")],
    solution="x",
    explanation="x",
    concepts=[],
)

SCRIPT_EXERCISE = Exercise(
    id="y",
    module="scripts",
    difficulty=1,
    title="y",
    description="y",
    examples="y",
    starter_code="y",
    hints=[],
    expected_behavior="y",
    hidden_tests=[
        HiddenTest(args=["14"], expected_stdout="I'm Even.", label="Even"),
        HiddenTest(args=["-5"], expected_stdout="I'm Odd.", label="Odd"),
    ],
    solution="y",
    explanation="y",
    concepts=[],
    exercise_type="script",
)


def test_student_stdout_never_contains_protocol_lines() -> None:
    code = (
        "def print_all(numbers):\n"
        "    for number in numbers:\n"
        "        print(number)\n"
    )
    result = run_submission(FUNCTION_EXERCISE, code)
    assert result.stdout.strip().splitlines() == ["1", "2"]
    assert "PYGYM_TEST_RESULT" not in result.stdout
    assert result.passed is True


def test_individual_test_outcomes_are_reported() -> None:
    code = (
        "def print_all(numbers):\n"
        "    for number in numbers:\n"
        "        print(number)\n"
    )
    result = run_submission(FUNCTION_EXERCISE, code)
    assert len(result.tests) == 1
    assert result.tests[0].passed is True


def test_stderr_is_reported_separately_on_exception() -> None:
    code = "def print_all(numbers):\n    raise ValueError('boom')\n"
    result = run_submission(FUNCTION_EXERCISE, code)
    assert result.passed is False
    assert result.status == "failed"
    assert "PYGYM_TEST_RESULT" not in result.stdout


def test_script_mode_runs_with_argv_and_checks_stdout() -> None:
    code = (
        "import sys\n\n"
        "n = int(sys.argv[1])\n"
        "if n % 2 == 0:\n"
        "    print(\"I'm Even.\")\n"
        "else:\n"
        "    print(\"I'm Odd.\")\n"
    )
    result = run_submission(SCRIPT_EXERCISE, code)
    assert result.passed is True
    assert result.tests_passed == 2
    assert [t.passed for t in result.tests] == [True, True]


def test_script_mode_reports_partial_failure() -> None:
    code = "import sys\nprint(\"I'm Even.\")\n"  # always says Even
    result = run_submission(SCRIPT_EXERCISE, code)
    assert result.passed is False
    assert result.tests_passed == 1
    assert result.status == "failed"


def test_script_mode_without_hidden_tests_just_runs() -> None:
    exercise = Exercise(
        id="z",
        module="scripts",
        difficulty=1,
        title="z",
        description="z",
        examples="z",
        starter_code="z",
        hints=[],
        expected_behavior="z",
        hidden_tests=[],
        solution="z",
        explanation="z",
        concepts=[],
        exercise_type="script",
    )
    result = run_submission(exercise, "print('hello')\n")
    assert result.stdout.strip() == "hello"
    assert result.tests == []
    assert result.status == "passed"
