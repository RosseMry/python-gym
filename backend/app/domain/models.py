"""Core domain entities for Python Gym.

These are plain dataclasses (not tied to FastAPI or SQLite) so the
domain stays independent from the delivery and storage mechanisms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ExerciseStatus(str, Enum):
    """Progress status of a single exercise for a given student.

    Only SOLVED or repeated successful attempts should count toward
    mastery (see spec section 21 - anti-copy mechanism).
    """

    NEW = "NEW"
    ATTEMPTED = "ATTEMPTED"
    SOLVED_WITH_HINT = "SOLVED_WITH_HINT"
    SOLVED = "SOLVED"
    MASTERED = "MASTERED"


@dataclass(frozen=True)
class HiddenTest:
    """A single hidden test case used to validate a submission."""

    call: str
    expected: str


@dataclass(frozen=True)
class Exercise:
    """A single practice exercise.

    Mirrors the structure described in spec section 18.
    """

    id: str
    module: str
    difficulty: int
    title: str
    description: str
    examples: str
    starter_code: str
    hints: list[str]
    expected_behavior: str
    hidden_tests: list[HiddenTest]
    solution: str
    explanation: str
    concepts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SubmissionResult:
    """Outcome of running a student's code against an exercise's tests."""

    passed: bool
    tests_total: int
    tests_passed: int
    stdout: str
    stderr: str
    error: str | None = None


@dataclass
class ProgressEntry:
    """Per-student, per-exercise progress record."""

    exercise_id: str
    status: ExerciseStatus
    attempts: int
    hints_used: int
    solution_revealed: bool
    last_submitted_at: str | None = None
