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
    # Sprint 3 finalization: optional per-hint link into the Function
    # Reference catalog (see FunctionReference below), same length as
    # ``hints`` when set, an entry being None means that hint has no
    # linked reference. Lets a hint that names e.g. sum() offer a
    # "Learn: sum()" popover without duplicating the explanation in
    # every exercise that happens to use it.
    hint_functions: list[str | None] | None = None


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


@dataclass(frozen=True)
class FunctionReference:
    """A reusable explanation of one Python builtin/concept.

    Sprint 3 finalization (spec sections 6-7): hints should teach which
    tool to reach for, then let the student open a reusable explanation
    instead of duplicating it in every exercise that happens to use the
    same function. Deliberately small and flat - this is not meant to
    grow into a full documentation system, just enough structure for a
    hint to reference a name and the UI to render it.
    """

    id: str
    name: str
    what_it_does: str
    syntax: str
    parameters: str
    return_value: str
    example: str
    example_output: str
    common_mistakes: str
    when_to_use: str
    related_exercise_ids: list[str] = field(default_factory=list)
    name_fr: str | None = None
    what_it_does_fr: str | None = None
    parameters_fr: str | None = None
    return_value_fr: str | None = None
    common_mistakes_fr: str | None = None
    when_to_use_fr: str | None = None


@dataclass
class ProgressEntry:
    """Per-student, per-exercise progress record."""

    exercise_id: str
    status: ExerciseStatus
    attempts: int
    hints_used: int
    solution_revealed: bool
    last_submitted_at: str | None = None


# ---------------------------------------------------------------------
# Sprint 4: SQL (spec sections 3-10)
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class SqlHiddenTest:
    """One hidden test for a SQL exercise.

    Two modes, chosen by whether ``check_query`` is set:

    - Empty ``check_query`` (the common case, for read-only/SELECT
      exercises): the student's OWN submitted query's result rows are
      compared against ``expected``. Rows are compared as an unordered
      multiset unless ``ordered=True`` (set for exercises that are
      specifically about row order, e.g. ORDER BY/LIMIT/OFFSET), since
      a student is not expected to add an ORDER BY they weren't asked
      for and SQL row order is otherwise unspecified.
    - Non-empty ``check_query`` (for mutating exercises - INSERT/
      UPDATE/DELETE): after the student's SQL executes, this separate,
      deterministic query re-reads the resulting table state and its
      rows are compared against ``expected`` - the only way to verify a
      mutation, since it returns no comparable result set of its own.

    ``expected`` is a ``repr()`` of a list of row tuples (the same
    "compare a repr string" convention as Python's HiddenTest).
    ``expect_error=True`` flips the check: the student's own submission
    is expected to raise (e.g. a CHECK/NOT NULL constraint correctly
    rejecting bad data).
    """

    check_query: str = ""
    expected: str = ""
    expect_error: bool = False
    label: str = ""
    ordered: bool = False


@dataclass(frozen=True)
class SqlExercise:
    """A single SQL practice exercise (spec section 4).

    Mirrors Exercise's shape (starter/hints/hidden_tests/solution/
    explanation) but for SQL: ``starter_query`` replaces starter_code,
    and grading runs against a real PostgreSQL fixture database instead
    of a Python subprocess (see sql_execution_service).
    """

    id: str
    module: str
    difficulty: int  # Level 1-5, spec section 10
    title: str
    description: str
    starter_query: str
    hints: list[str]
    expected_behavior: str
    hidden_tests: list[SqlHiddenTest]
    solution: str
    explanation: str
    concepts: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    source: str = "python_gym_sql"
    postgres_note: str | None = None
    prerequisites: list[str] = field(default_factory=list)
    exercise_status: str = "active"
    title_fr: str | None = None
    description_fr: str | None = None
    explanation_fr: str | None = None
    hints_fr: list[str] | None = None


@dataclass(frozen=True)
class SqlSubmissionResult:
    """Outcome of running a student's SQL against an exercise's tests."""

    status: str  # "passed", "failed", "error"
    passed: bool
    tests_total: int
    tests_passed: int
    tests: list[TestOutcome]
    result_columns: list[str]
    result_rows: list[list[str]]
    error: str | None
    execution_time: float


@dataclass(frozen=True)
class SqlLearningNote:
    """A theory page for one SQL topic (spec section 3).

    Structured after freeCodeCamp's relational-database course (used as
    the primary source for explanations/terminology/progression, not
    copied verbatim - see each note's ``source``), with a
    ``postgres_note`` field the equivalent Python LearningNote doesn't
    need, since SQL syntax genuinely varies by database engine and this
    project teaches PostgreSQL specifically (spec section 5).
    """

    id: str
    module: str
    title: str
    display_order: int
    what_is_it: str
    why_it_matters: str
    syntax: str
    example: str
    output: str
    common_mistakes: str
    mini_exercise: str
    postgres_note: str | None = None
    source: str = "freecodecamp"
    related_exercise_ids: list[str] = field(default_factory=list)
    title_fr: str | None = None
    what_is_it_fr: str | None = None
    why_it_matters_fr: str | None = None
    syntax_fr: str | None = None
    common_mistakes_fr: str | None = None
    mini_exercise_fr: str | None = None


# ---------------------------------------------------------------------
# Sprint 4: Timed Exam (spec section 2)
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class ExamQuestion:
    """One question in the exam question bank.

    ``kind`` is one of "mcq", "output_prediction", "debugging", or
    "coding" - these are internal categories, never separate sidebar
    entries or exercise types (spec: "Those categories must NOT become
    navigation items"). Coding questions reuse the existing Python
    ``HiddenTest``/``run_submission`` machinery directly rather than a
    parallel grading path.
    """

    id: str
    kind: str
    category: str
    prompt: str
    difficulty: int
    points: int = 1
    code_snippet: str | None = None
    starter_code: str | None = None
    choices: list[str] | None = None
    correct_choice: int | None = None
    expected_output: str | None = None
    hidden_tests: list[HiddenTest] | None = None
    solution: str | None = None
    explanation: str = ""
    source: str = "adapted"


@dataclass(frozen=True)
class ExamSession:
    """One timed attempt: a fixed question set and a server-side deadline.

    The deadline is computed and stored server-side at creation time
    (``deadline_at``) - the client only ever displays a countdown to
    it, never supplies or extends it, so a manipulated client clock
    can't grant extra time (spec section 2's timed behavior).
    """

    id: str
    question_ids: list[str]
    started_at: str
    duration_seconds: int
    deadline_at: str
    status: str = "in_progress"  # "in_progress", "submitted", "timed_out"
    answers: dict[str, str] = field(default_factory=dict)
    submitted_at: str | None = None
    score: float | None = None
    max_score: float | None = None


@dataclass(frozen=True)
class ExamAnswerResult:
    """Per-question grading detail shown on the results screen."""

    question_id: str
    correct: bool
    points_earned: int
    points_possible: int


@dataclass(frozen=True)
class ExamResult:
    """The evaluation shown after submit/timeout (spec section 2)."""

    session_id: str
    status: str
    score: float
    max_score: float
    questions_total: int
    questions_correct: int
    time_used_seconds: int
    answers: list[ExamAnswerResult]
