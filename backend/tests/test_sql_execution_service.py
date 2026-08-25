"""Tests for grading student SQL against the isolated Postgres fixtures.

Requires the fixtures schema to be provisioned (scripts/provision_sql_
fixtures.py) against a reachable SQL_DATABASE_URL - the same live,
throwaway Postgres instance the app itself uses for SQL grading.
"""

from __future__ import annotations

from app.domain.models import SqlExercise, SqlHiddenTest
from app.services.sql_execution_service import run_sql_submission

SELECT_EXERCISE = SqlExercise(
    id="x-select",
    module="foundations",
    difficulty=1,
    title="x",
    description="x",
    starter_query="-- your query here\n",
    hints=[],
    expected_behavior="x",
    # Filtered to a fixed set of ids so this test doesn't depend on the
    # exact total set of departments in the shared fixtures.
    hidden_tests=[
        SqlHiddenTest(
            expected=repr(
                sorted([["Engineering"], ["Sales"], ["Support"], ["Marketing"]])
            ),
        ),
    ],
    solution="SELECT name FROM departments WHERE id IN (1, 2, 3, 4);",
    explanation="x",
    concepts=[],
)

ORDERED_EXERCISE = SqlExercise(
    id="x-ordered",
    module="foundations",
    difficulty=1,
    title="x",
    description="x",
    starter_query="-- your query here\n",
    hints=[],
    expected_behavior="x",
    hidden_tests=[
        SqlHiddenTest(
            expected=repr([["Engineering"], ["Marketing"], ["Support"], ["Sales"]]),
            ordered=True,
        ),
    ],
    solution=(
        "SELECT name FROM departments WHERE id IN (1, 2, 3, 4) "
        "ORDER BY length(name) DESC, name;"
    ),
    explanation="x",
    concepts=[],
)

MUTATION_EXERCISE = SqlExercise(
    id="x-mutate",
    module="foundations",
    difficulty=2,
    title="x",
    description="x",
    starter_query="-- your query here\n",
    hints=[],
    expected_behavior="x",
    hidden_tests=[
        SqlHiddenTest(
            check_query="SELECT name FROM departments WHERE name = 'Legal'",
            expected=repr([["Legal"]]),
        ),
    ],
    solution="INSERT INTO departments (name) VALUES ('Legal');",
    explanation="x",
    concepts=[],
)


def test_correct_select_passes() -> None:
    result = run_sql_submission(SELECT_EXERCISE, SELECT_EXERCISE.solution)
    assert result.passed is True
    assert result.tests_passed == 1


def test_no_op_starter_query_fails() -> None:
    """Regression: hidden tests must grade the student's OWN result, not
    an independently re-run "correct" query - a no-op starter query must
    not trivially pass just because it doesn't error.
    """
    result = run_sql_submission(SELECT_EXERCISE, SELECT_EXERCISE.starter_query)
    assert result.passed is False


def test_wrong_columns_fails() -> None:
    result = run_sql_submission(SELECT_EXERCISE, "SELECT id FROM departments;")
    assert result.passed is False


def test_unordered_comparison_ignores_row_order() -> None:
    # Same rows as the solution but selected via a different, still
    # correct, WHERE-based query that returns them in a different order.
    result = run_sql_submission(
        SELECT_EXERCISE,
        "SELECT name FROM departments WHERE id IN (4, 3, 2, 1);",
    )
    assert result.passed is True


def test_ordered_test_requires_matching_order() -> None:
    result = run_sql_submission(ORDERED_EXERCISE, ORDERED_EXERCISE.solution)
    assert result.passed is True


def test_ordered_test_fails_on_wrong_order() -> None:
    result = run_sql_submission(
        ORDERED_EXERCISE, "SELECT name FROM departments ORDER BY name;"
    )
    assert result.passed is False


def test_invalid_sql_reports_error_not_crash() -> None:
    result = run_sql_submission(SELECT_EXERCISE, "SELEKT name FROM departments;")
    assert result.status == "error"
    assert result.passed is False
    assert result.error is not None


def test_mutation_is_graded_by_resulting_state() -> None:
    result = run_sql_submission(MUTATION_EXERCISE, MUTATION_EXERCISE.solution)
    assert result.passed is True


def test_mutation_is_rolled_back_and_does_not_persist() -> None:
    run_sql_submission(MUTATION_EXERCISE, MUTATION_EXERCISE.solution)
    # A second, independent submission must see the same starting state -
    # the department must NOT have been permanently inserted.
    result = run_sql_submission(MUTATION_EXERCISE, MUTATION_EXERCISE.solution)
    assert result.passed is True


def test_destructive_submission_is_rolled_back() -> None:
    destructive = SqlExercise(
        id="x-drop",
        module="foundations",
        difficulty=1,
        title="x",
        description="x",
        starter_query="-- your query here\n",
        hints=[],
        expected_behavior="x",
        hidden_tests=[
            SqlHiddenTest(
                expected=repr(
                    sorted([["Engineering"], ["Sales"], ["Support"], ["Marketing"]])
                ),
            ),
        ],
        solution="DROP TABLE departments CASCADE;",
        explanation="x",
        concepts=[],
    )
    drop_result = run_sql_submission(destructive, destructive.solution)
    assert drop_result.error is None  # DROP TABLE itself succeeds...
    assert drop_result.passed is False  # ...but leaves no rows to compare.

    # departments must still exist and be intact for the next submission -
    # the DROP was rolled back, never committed.
    followup = run_sql_submission(SELECT_EXERCISE, SELECT_EXERCISE.solution)
    assert followup.passed is True


CONSTRAINT_EXERCISE = SqlExercise(
    id="x-expect-error",
    module="relational",
    difficulty=1,
    title="x",
    description="x",
    starter_query="-- your query here\n",
    hints=[],
    expected_behavior="x",
    hidden_tests=[SqlHiddenTest(expect_error=True)],
    solution=(
        "INSERT INTO customers "
        "(first_name, last_name, email, city, country, signup_date) "
        "VALUES ('Test', 'User', 'ana.silva@example.com', "
        "'Lisbon', 'Portugal', '2024-01-01');"
    ),
    explanation="x",
    concepts=[],
)


def test_expect_error_passes_when_student_query_raises() -> None:
    """Regression: a savepoint must let grading continue after the
    student's OWN query raises, so an ``expect_error`` test - e.g. "this
    INSERT should violate a UNIQUE constraint" - can actually pass.
    Before the savepoint fix, any raised error short-circuited to
    status="error" before hidden tests ran, so expect_error tests could
    never pass.
    """
    result = run_sql_submission(CONSTRAINT_EXERCISE, CONSTRAINT_EXERCISE.solution)
    assert result.passed is True
    assert result.tests_passed == 1


def test_expect_error_fails_when_student_query_does_not_raise() -> None:
    result = run_sql_submission(
        CONSTRAINT_EXERCISE, CONSTRAINT_EXERCISE.starter_query
    )
    assert result.passed is False


def test_expect_error_fixture_data_is_intact_afterward() -> None:
    run_sql_submission(CONSTRAINT_EXERCISE, CONSTRAINT_EXERCISE.solution)
    # The savepoint rollback plus the outer transaction rollback must
    # leave the fixtures exactly as they were - re-running must still
    # hit the same UNIQUE violation, not "email already free."
    result = run_sql_submission(CONSTRAINT_EXERCISE, CONSTRAINT_EXERCISE.solution)
    assert result.passed is True


APPOINTMENT_COUNT_EXERCISE = SqlExercise(
    id="x-appointment-count",
    module="transactions",
    difficulty=1,
    title="x",
    description="x",
    starter_query="-- your query here\n",
    hints=[],
    expected_behavior="x",
    hidden_tests=[
        SqlHiddenTest(
            check_query="SELECT COUNT(*) FROM appointments",
            expected=repr([["7"]]),
        ),
    ],
    solution="SELECT 1;",
    explanation="x",
    concepts=[],
)


def test_literal_commit_is_rejected_before_execution() -> None:
    """Regression: a literal COMMIT in student SQL used to permanently
    commit the ambient grading transaction - including any DML the
    student ran just before it - straight into the SHARED fixture
    database, bypassing the "always rolled back" safety guarantee
    entirely. It must now be rejected before anything runs.
    """
    exercise = SqlExercise(
        id="x-commit-danger",
        module="transactions",
        difficulty=1,
        title="x",
        description="x",
        starter_query="-- your query here\n",
        hints=[],
        expected_behavior="x",
        hidden_tests=[SqlHiddenTest(expected=repr([]))],
        solution="DELETE FROM appointments; COMMIT;",
        explanation="x",
        concepts=[],
    )
    result = run_sql_submission(exercise, exercise.solution)
    assert result.status == "error"
    assert result.passed is False
    assert "COMMIT" in result.error

    # The DELETE must never have taken effect - the whole submission was
    # rejected before any statement ran.
    followup = run_sql_submission(
        APPOINTMENT_COUNT_EXERCISE, APPOINTMENT_COUNT_EXERCISE.solution
    )
    assert followup.passed is True


def test_bare_rollback_is_rejected() -> None:
    exercise = SqlExercise(
        id="x-rollback-danger",
        module="transactions",
        difficulty=1,
        title="x",
        description="x",
        starter_query="-- your query here\n",
        hints=[],
        expected_behavior="x",
        hidden_tests=[SqlHiddenTest(expected=repr([]))],
        solution="ROLLBACK;",
        explanation="x",
        concepts=[],
    )
    result = run_sql_submission(exercise, exercise.solution)
    assert result.status == "error"
    assert result.passed is False


def test_rollback_to_savepoint_is_allowed() -> None:
    """ROLLBACK TO SAVEPOINT is safe (it stays inside the ambient
    transaction) and is needed for real Transactions exercises - it
    must NOT be caught by the bare-ROLLBACK guard.
    """
    solution = "SAVEPOINT sp1; DELETE FROM appointments; ROLLBACK TO SAVEPOINT sp1;"
    exercise = SqlExercise(
        id="x-savepoint-ok",
        module="transactions",
        difficulty=1,
        title="x",
        description="x",
        starter_query="-- your query here\n",
        hints=[],
        expected_behavior="x",
        hidden_tests=[
            SqlHiddenTest(
                check_query="SELECT COUNT(*) FROM appointments",
                expected=repr([["7"]]),
            ),
        ],
        solution=solution,
        explanation="x",
        concepts=[],
    )
    result = run_sql_submission(exercise, exercise.solution)
    assert result.status == "passed"
    assert result.passed is True


def test_plpgsql_function_body_end_is_not_blocked() -> None:
    """A PL/pgSQL function/procedure/trigger body legitimately ends in
    ``END;`` inside its $$-quoted definition - that must not trip the
    same guard that blocks a real top-level END (a COMMIT synonym).
    """
    solution = (
        "CREATE FUNCTION x_double(n INTEGER) RETURNS INTEGER AS $$\n"
        "BEGIN\n"
        "    RETURN n * 2;\n"
        "END;\n"
        "$$ LANGUAGE plpgsql;"
    )
    exercise = SqlExercise(
        id="x-plpgsql-ok",
        module="functions",
        difficulty=3,
        title="x",
        description="x",
        starter_query="-- your query here\n",
        hints=[],
        expected_behavior="x",
        hidden_tests=[
            SqlHiddenTest(check_query="SELECT x_double(21)", expected=repr([["42"]])),
        ],
        solution=solution,
        explanation="x",
        concepts=[],
    )
    result = run_sql_submission(exercise, exercise.solution)
    assert result.status == "passed"
    assert result.passed is True
