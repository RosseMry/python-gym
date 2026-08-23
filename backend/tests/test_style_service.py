"""Tests for the style/lint check used by 42-piscine-profile exercises."""

from __future__ import annotations

from app.services.style_service import check_style


def test_clean_code_passes_style_check() -> None:
    code = (
        "def add(a, b):\n"
        '    """Add two numbers."""\n'
        "    return a + b\n"
    )
    ran, passed, output = check_style(code)
    assert ran is True
    assert passed is True
    assert output == ""


def test_bad_style_fails_and_reports_output() -> None:
    code = "def add(a,b):\n  return a+b\n"  # missing space, bad indent
    ran, passed, output = check_style(code)
    assert ran is True
    assert passed is False
    assert output != ""


def test_style_check_never_raises_on_syntax_errors() -> None:
    code = "def broken(:\n"
    ran, passed, output = check_style(code)
    assert ran is True
    assert passed is False
