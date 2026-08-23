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

    Sprint 2 adds two states (Python-Gym Sprint 2 spec, sections 3-4,8):

    - FAILED: the student attempted and has not solved it yet.
    - SOLVED_TO_REPEAT: the student solved it, but explicitly asked to
      practice it again later. This is NOT mastery, and is distinct
      from FAILED - the exercise *was* solved.

    Sprint 3 correction splits what used to be one SOLVED_WITH_HINT
    value into two, since "used a hint" and "revealed the full
    solution" are different signals for the future adaptive/exam
    system: SOLVED_WITH_HINT (a hint was used) and
    SOLVED_AFTER_SOLUTION (the solution was revealed before passing).
    Neither counts toward mastery on that same pass.
    """

    NEW = "NEW"
    ATTEMPTED = "ATTEMPTED"
    FAILED = "FAILED"
    SOLVED_WITH_HINT = "SOLVED_WITH_HINT"
    SOLVED_AFTER_SOLUTION = "SOLVED_AFTER_SOLUTION"
    SOLVED = "SOLVED"
    SOLVED_TO_REPEAT = "SOLVED_TO_REPEAT"
    MASTERED = "MASTERED"


@dataclass(frozen=True)
class HiddenTest:
    """A single hidden test case used to validate a submission.

    Two mutually exclusive modes (Sprint 2 spec section 14 - the system
    must support both function-based and script-based exercises):

    - call mode (Sprint 1 default): ``call`` is a Python expression
      (e.g. ``solve([1, 2, 3])``) and ``expected`` is compared against
      ``repr()`` of its result.
    - script mode (Sprint 2): the student's file is run as a whole
      program with ``args`` as ``sys.argv[1:]`` and optional ``stdin``,
      and its full stdout is compared against ``expected_stdout``.
    """

    call: str = ""
    expected: str = ""
    args: list[str] | None = None
    stdin: str | None = None
    expected_stdout: str | None = None
    label: str = ""

    @property
    def is_script_mode(self) -> bool:
        """Whether this test runs the file as a script rather than a call."""
        return self.args is not None


@dataclass(frozen=True)
class Exercise:
    """A single practice exercise.

    Mirrors the structure described in spec section 18, extended in
    Sprint 2 (section 17) with metadata needed for multiple content
    sources, learning tracks, and validation profiles.
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
    # Sprint 2 metadata (spec sections 17-21, 26, 29-33):
    track: str = "python"
    source: str = "progressive_python"
    skills: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    validation_profile: str = "standard_python"
    exercise_type: str = "function"  # "function" or "script"
    # "active" (normal), "excluded" (never part of the learning path,
    # e.g. the Piscine compression exercise), or "locked" (a real,
    # named exercise that can't run yet because its prerequisite track
    # - e.g. NumPy/Pandas - doesn't exist; still shown in the catalog,
    # unlike "excluded").
    exercise_status: str = "active"
    # Sprint 3 correction: which day/level of 30 Days of Python this
    # came from, when source="30_days_of_python". None for every other
    # source.
    day: int | None = None
    level: int | None = None
    # Sprint 3 French translations, all optional. Only user-facing
    # prose is translated - starter_code/solution stay code, and
    # concepts/skills stay English taxonomy keys (the frontend maps
    # those to display labels per locale instead). Empty/None means
    # "not translated yet" - the frontend falls back to the English
    # field rather than showing a blank.
    title_fr: str | None = None
    description_fr: str | None = None
    examples_fr: str | None = None
    expected_behavior_fr: str | None = None
    explanation_fr: str | None = None
    hints_fr: list[str] | None = None


@dataclass(frozen=True)
class TestOutcome:
    """The pass/fail result of a single hidden test, for UI display."""

    label: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class StyleCheckResult:
    """Result of a style/lint validation (e.g. flake8), separate from tests."""

    ran: bool
    passed: bool
    output: str = ""


@dataclass(frozen=True)
class SubmissionResult:
    """Outcome of running a student's code against an exercise's tests.

    Sprint 2 (spec sections 10-15) requires the student to clearly see
    their own program's output, separate from stderr, from individual
    test outcomes, and from any hidden-test internals.
    """

    status: str  # "passed", "failed", "error"
    passed: bool
    tests_total: int
    tests_passed: int
    tests: list[TestOutcome]
    stdout: str
    stderr: str
    result: str | None
    execution_time: float
    error: str | None = None
    style: StyleCheckResult | None = None


@dataclass(frozen=True)
class LearningNote:
    """A theory page for one Python topic (spec: Learning Notes).

    Deliberately structured (not one markdown blob) so the frontend can
    render each section on its own: explanation, then syntax, then
    examples, then common mistakes, then a mini exercise, then links to
    real practice exercises for the topic.
    """

    id: str
    module: str
    title: str
    display_order: int
    explanation: str
    syntax: str
    examples: str
    common_mistakes: str
    mini_exercise: str
    related_exercise_ids: list[str] = field(default_factory=list)
    title_fr: str | None = None
    explanation_fr: str | None = None
    syntax_fr: str | None = None
    examples_fr: str | None = None
    common_mistakes_fr: str | None = None
    mini_exercise_fr: str | None = None


@dataclass
class ProgressEntry:
    """Per-student, per-exercise progress record."""

    exercise_id: str
    status: ExerciseStatus
    attempts: int
    hints_used: int
    solution_revealed: bool
    last_submitted_at: str | None = None
