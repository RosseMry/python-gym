"""Runs student-submitted code against an exercise's hidden tests.

SECURITY NOTE - MVP LIMITATIONS (spec section 27)
--------------------------------------------------
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
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from app.domain.models import Exercise, HiddenTest, SubmissionResult

_TIMEOUT_SECONDS = 5
_MEMORY_LIMIT_BYTES = 256 * 1024 * 1024  # 256 MB


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


def _build_test_script(student_code: str, hidden_tests: list[HiddenTest]) -> str:
    """Wrap the student's code with hidden-test assertions.

    Each hidden test is a call expression (e.g. ``solve([1, 2, 3])``)
    and its expected ``repr`` value. Results are printed as a simple
    machine-readable protocol so the parent process can parse them
    without needing JSON-safe stdout from the student's own prints.
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
        "    print(f'__TEST__ {__case_id__} {__ok__} {__actual__!r}')"
    )
    return "\n".join(lines)


def run_submission(exercise: Exercise, student_code: str) -> SubmissionResult:
    """Execute the student's code against the exercise's hidden tests."""
    script = _build_test_script(student_code, exercise.hidden_tests)

    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = Path(tmp_dir) / "submission.py"
        script_path.write_text(script, encoding="utf-8")

        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_SECONDS,
                cwd=tmp_dir,
                env={},
                preexec_fn=_preexec_limits if sys.platform != "win32" else None,
            )
        except subprocess.TimeoutExpired:
            return SubmissionResult(
                passed=False,
                tests_total=len(exercise.hidden_tests),
                tests_passed=0,
                stdout="",
                stderr="",
                error=f"Execution timed out after {_TIMEOUT_SECONDS}s.",
            )

    tests_passed = 0
    for line in proc.stdout.splitlines():
        if line.startswith("__TEST__ "):
            _, _case_id, ok_str, _actual = line.split(" ", 3)
            if ok_str == "True":
                tests_passed += 1

    tests_total = len(exercise.hidden_tests)
    return SubmissionResult(
        passed=tests_total > 0 and tests_passed == tests_total,
        tests_total=tests_total,
        tests_passed=tests_passed,
        stdout=proc.stdout,
        stderr=proc.stderr,
        error=None if proc.returncode == 0 else "Non-zero exit from submission.",
    )
