"""Runs flake8 against submitted code, kept separate from hidden tests.

Sprint 2 spec section 32: the 42 Piscine uses flake8 ("norminette") as
part of its style rules, but this must never be silently mixed into
the hidden-test result - it's surfaced as its own ``style`` field, and
only for exercises whose ``validation_profile`` is ``42_piscine``
(spec section 30 - standard exercises are not affected).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_TIMEOUT_SECONDS = 5


def check_style(code: str) -> tuple[bool, bool, str]:
    """Run flake8 on ``code``. Returns (ran, passed, output).

    ``ran`` is False when flake8 isn't installed in this environment,
    so the caller can show "style check unavailable" instead of a
    false pass. This never raises - a missing or broken flake8 should
    not break submission grading.
    """
    if shutil.which("flake8") is None:
        return False, False, "flake8 is not installed in this environment."

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / "submission.py"
        path.write_text(code, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "flake8", str(path)],
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return True, False, "Style check timed out."
        except OSError as exc:
            return False, False, f"Could not run flake8: {exc}"

        output = proc.stdout.replace(str(path), "submission.py")
        return True, proc.returncode == 0, output.strip()
