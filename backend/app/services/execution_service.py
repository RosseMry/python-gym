"""Runs student-submitted code against an exercise's hidden tests.

SECURITY NOTE - MVP LIMITATIONS (spec section 27, unchanged in Sprint 2
section 41 - the sandbox is not to be rebuilt this sprint)
--------------------------------------------------------------------
Arbitrary Python code from the student is executed as a subprocess,
not inside the main FastAPI process. For this MVP the isolation is:

- a separate ``python`` subprocess (not the FastAPI worker),
- a wall-clock timeout,
- a stripped-down environment (no inherited env vars / secrets),
- resource limits (CPU time, memory, no forked children) via the
  ``resource`` module on POSIX systems.

This is NOT a real security sandbox. It does not stop:
- reading/writing the local filesystem the subprocess user can reach,
- opening network connections,
- exhausting disk space.

For anything beyond local, single-user practice, this must be
replaced with a proper sandbox (e.g. gVisor, Docker with a locked-down
seccomp profile and no network, or a service like Piston/Judge0)
before the platform is exposed to untrusted users.

SPRINT 2 CHANGES (see Python-Gym Sprint 2 spec, sections 10-15)
----------------------------------------------------------------
Sprint 1 printed a machine-readable ``__TEST__`` protocol straight to
the same stdout the student's own ``print()`` calls used, and never
separated the two before handing stdout back to the API layer. Sprint
2 fixes this: the protocol lines are now tagged with an out-of-band
sentinel the student could not plausibly produce by accident, and
``run_submission`` strips them out before returning ``stdout`` - the
student now only ever sees their own program's output.

This module also now supports two independent test modes on the same
``Exercise`` (spec section 14):

- **function mode** (Sprint 1): hidden tests are Python call
  expressions checked against ``repr()`` of their return value, all
  executed in one process alongside the student's function/class
  definitions.
- **script mode** (Sprint 2): the student's file is executed as a
  whole program (``__main__``), once per hidden test, with that test's
  ``args`` as ``sys.argv[1:]`` and optional ``stdin`` piped in; its
  full stdout is compared against ``expected_stdout``. This matches
  how many 42 Piscine exercises are actually structured (e.g.
  ``python whatis.py 14``).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app.domain.models import Exercise, HiddenTest, SubmissionResult, TestOutcome

_TIMEOUT_SECONDS = 5
_MEMORY_LIMIT_BYTES = 256 * 1024 * 1024  # 256 MB

# A sentinel a student's own print() output could not plausibly produce
# by accident, used to tag the hidden-test protocol lines so they can be
# stripped out of the stdout shown to the student (Sprint 2 section 11).
# Deliberately plain ASCII with no control characters: some of the
# obvious control-character choices (e.g. \x1e) are themselves treated
# as line separators by str.splitlines(), which would silently break
# the tag apart before we ever get to check line prefixes.
_PROTOCOL_TAG = "###PYGYM_TEST_RESULT###"


def _preexec_limits() -> None:
    """Apply CPU/memory limits inside the child process (POSIX only)."""
    try:
        import resource

        resource.setrlimit(
            resource.RLIMIT_CPU, (_TIMEOUT_SECONDS, _TIMEOUT_SECONDS)
        )
        resource.setrlimit(
            resource.RLIMIT_AS, (_MEMORY_LIMIT_BYTES, _MEMORY_LIMIT_BYTES)
        )
    except ImportError:
        # resource module is POSIX-only (no-op on Windows for the MVP).
        pass


def _run_subprocess(
    script_path: Path, args: list[str], stdin_text: str | None
) -> subprocess.CompletedProcess[str] | None:
    """Run one Python file as a subprocess. Returns None on timeout.

    ``PYTHONHASHSEED=0`` is set so that any set/dict ordering that
    depends on string hash randomization (which set literals do) is
    reproducible across runs - otherwise hidden tests that print a set
    would flake depending on the interpreter's random hash seed.
    """
    try:
        return subprocess.run(
            [sys.executable, "-I", str(script_path), *args],
            input=stdin_text if stdin_text is not None else "",
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            cwd=script_path.parent,
            env={"PYTHONHASHSEED": "0"},
            preexec_fn=_preexec_limits if sys.platform != "win32" else None,
        )
    except subprocess.TimeoutExpired:
        return None


def _build_function_mode_script(
    student_code: str, hidden_tests: list[HiddenTest]
) -> str:
    """Wrap the student's code with hidden-test assertions.

    Each hidden test is a call expression (e.g. ``solve([1, 2, 3])``)
    and its expected ``repr`` value. Results are printed tagged with
    ``_PROTOCOL_TAG`` so they can be told apart from the student's own
    output.
    """
    lines = [student_code, "", "__results__ = []"]
    for i, test in enumerate(hidden_tests):
        lines.append(
            f"try:\n"
            f"    __actual__ = repr({test.call})\n"
            f"    __ok__ = __actual__ == {test.expected!r}\n"
            f"    __results__.append(('{i}', __ok__, __actual__))\n"
            f"except Exception as __e__:\n"
            f"    __results__.append(('{i}', False, f'ERROR: {{__e__}}'))"
        )
    lines.append("")
    lines.append("for __case_id__, __ok__, __actual__ in __results__:")
    lines.append(
        f"    print(f'{_PROTOCOL_TAG}{{__case_id__}}\\t{{__ok__}}\\t{{__actual__!r}}')"
    )
    return "\n".join(lines)


def _split_protocol_lines(raw_stdout: str) -> tuple[str, list[str]]:
    """Split raw stdout into (student_stdout, protocol_lines).

    Splits on plain ``\\n`` rather than ``str.splitlines()``, since the
    latter also breaks on several unicode line-boundary characters
    that could otherwise appear inside student output or the tag.
    """
    student_lines = []
    protocol_lines = []
    for line in raw_stdout.split("\n"):
        if line.startswith(_PROTOCOL_TAG):
            protocol_lines.append(line[len(_PROTOCOL_TAG):])
        else:
            student_lines.append(line)
    return "\n".join(student_lines), protocol_lines


def _run_function_mode(exercise: Exercise, student_code: str) -> SubmissionResult:
    """Run all call-mode hidden tests in a single shared process."""
    script = _build_function_mode_script(student_code, exercise.hidden_tests)
    tests_total = len(exercise.hidden_tests)

    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "submission.py"
        script_path.write_text(script, encoding="utf-8")

        start = time.perf_counter()
        proc = _run_subprocess(script_path, [], None)
        elapsed = time.perf_counter() - start

    if proc is None:
        return SubmissionResult(
            status="error",
            passed=False,
            tests_total=tests_total,
            tests_passed=0,
            tests=[],
            stdout="",
            stderr="",
            result=None,
            execution_time=_TIMEOUT_SECONDS,
            error=f"Execution timed out after {_TIMEOUT_SECONDS}s.",
        )

    student_stdout, protocol_lines = _split_protocol_lines(proc.stdout)

    tests: list[TestOutcome] = []
    last_result: str | None = None
    for i, line in enumerate(protocol_lines):
        case_id, ok_str, actual = line.split("\t", 2)
        passed = ok_str == "True"
        label = exercise.hidden_tests[i].label or f"Test {int(case_id) + 1}"
        tests.append(TestOutcome(label=label, passed=passed, detail=actual))
        last_result = actual

    tests_passed = sum(1 for t in tests if t.passed)
    exit_ok = proc.returncode == 0
    all_passed = tests_total > 0 and tests_passed == tests_total and exit_ok

    if not exit_ok and not protocol_lines:
        status = "error"
    elif all_passed:
        status = "passed"
    else:
        status = "failed"

    return SubmissionResult(
        status=status,
        passed=all_passed,
        tests_total=tests_total,
        tests_passed=tests_passed,
        tests=tests,
        stdout=student_stdout,
        stderr=proc.stderr,
        result=last_result,
        execution_time=elapsed,
        error=None if exit_ok else "Non-zero exit from submission.",
    )


def _run_script_mode(exercise: Exercise, student_code: str) -> SubmissionResult:
    """Run the student's file as a whole program, once per hidden test."""
    tests: list[TestOutcome] = []
    combined_stdout_parts: list[str] = []
    combined_stderr_parts: list[str] = []
    total_time = 0.0
    timed_out = False
    any_nonzero_without_test_data = False

    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "submission.py"
        script_path.write_text(student_code, encoding="utf-8")

        cases = exercise.hidden_tests or [HiddenTest(args=[], expected_stdout=None)]
        for i, test in enumerate(cases):
            start = time.perf_counter()
            proc = _run_subprocess(script_path, test.args or [], test.stdin)
            total_time += time.perf_counter() - start

            label = test.label or f"Test {i + 1}"
            if proc is None:
                timed_out = True
                tests.append(TestOutcome(label=label, passed=False, detail="timeout"))
                continue

            combined_stdout_parts.append(proc.stdout)
            if proc.stderr:
                combined_stderr_parts.append(proc.stderr)

            if test.expected_stdout is None:
                # No hidden tests for this exercise (e.g. non-deterministic
                # output like current date/time) - just run it and show
                # output, without asserting pass/fail.
                continue

            passed = proc.stdout.rstrip("\n") == test.expected_stdout.rstrip("\n")
            if proc.returncode != 0 and not passed:
                any_nonzero_without_test_data = True
            tests.append(TestOutcome(label=label, passed=passed, detail=proc.stdout))

    tests_passed = sum(1 for t in tests if t.passed)
    tests_total = len(tests) if exercise.hidden_tests else 0
    all_passed = tests_total > 0 and tests_passed == tests_total and not timed_out

    if timed_out:
        status = "error"
        error = f"Execution timed out after {_TIMEOUT_SECONDS}s."
    elif tests_total == 0:
        status = "passed"
        error = None
    elif all_passed:
        status = "passed"
        error = None
    elif any_nonzero_without_test_data:
        status = "error"
        error = "Non-zero exit from submission."
    else:
        status = "failed"
        error = None

    return SubmissionResult(
        status=status,
        passed=all_passed if tests_total else True,
        tests_total=tests_total,
        tests_passed=tests_passed,
        tests=tests,
        stdout="\n".join(combined_stdout_parts),
        stderr="\n".join(combined_stderr_parts),
        result=None,
        execution_time=total_time,
        error=error,
    )


def run_submission(exercise: Exercise, student_code: str) -> SubmissionResult:
    """Execute the student's code against the exercise's hidden tests.

    Dispatches to function mode or script mode based on
    ``exercise.exercise_type`` (spec section 14).
    """
    if exercise.exercise_type == "script":
        return _run_script_mode(exercise, student_code)
    return _run_function_mode(exercise, student_code)
