"""Generates Progressive Python (bridge) and 30 Days of Python exercises.

Progressive Python exercises bridge the gap between Sprint 1's for-loop
levels (which stopped at Level 7 - enumerate) and 42 Piscine exercises,
per Sprint 2 spec section 24: nested loops were explicitly deferred in
Sprint 1 ("Only introduce after the previous levels are mastered").

30 Days of Python exercises are adapted from Asabeneh Yetayeh's
"30 Days of Python" (https://github.com/Asabeneh/30-Days-Of-Python),
Day 3 - Operators exercises #4 and #21 (fetched from the real repo,
not invented). Statements are paraphrased in our own words per
copyright practice, but the numbers/behaviour match the source
exactly.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _write(directory: Path, exercises: list[dict]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for exercise in exercises:
        out_path = directory / f"{exercise['id']}.json"
        out_path.write_text(
            json.dumps(exercise, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out_path.relative_to(ROOT)}")


PROGRESSIVE_EXERCISES: list[dict] = [
    {
        "id": "prog-nested-loop-001",
        "module": "for_loops",
        "difficulty": 4,
        "title": "Multiplication table (nested loops)",
        "description": (
            "Write a function `multiplication_table(n)` that returns a "
            "list of lists: row `i` (for i from 1 to n) contains "
            "`[i*1, i*2, ..., i*n]`.\n\n"
            "This is the bridge exercise from Sprint 1's for-loop "
            "levels (which stopped before nested loops) toward the 42 "
            "Piscine's own multi-column table exercise."
        ),
        "examples": "multiplication_table(3) -> [[1, 2, 3], [2, 4, 6], [3, 6, 9]]",
        "starter_code": (
            "def multiplication_table(n):\n    # write your code here\n    pass\n"
        ),
        "hints": [
            "You need one loop to build each row, and another loop "
            "inside it to fill in that row's columns - a loop inside a "
            "loop.",
            "The outer loop picks the row number (1..n); the inner loop, "
            "using that same row number, computes each column value "
            "(row * column).",
            "rows = []\nfor row in range(1, n + 1):\n    this_row = []\n"
            "    for col in range(1, n + 1):\n        this_row.append("
            "row * col)\n    rows.append(this_row)\nreturn rows",
        ],
        "expected_behavior": "Returns an n-by-n list of lists of the multiplication table.",
        "hidden_tests": [
            {"call": "multiplication_table(3)", "expected": "[[1, 2, 3], [2, 4, 6], [3, 6, 9]]"},
            {"call": "multiplication_table(1)", "expected": "[[1]]"},
            {"call": "multiplication_table(2)", "expected": "[[1, 2], [2, 4]]"},
        ],
        "solution": (
            "def multiplication_table(n):\n"
            "    rows = []\n"
            "    for row in range(1, n + 1):\n"
            "        this_row = []\n"
            "        for col in range(1, n + 1):\n"
            "            this_row.append(row * col)\n"
            "        rows.append(this_row)\n"
            "    return rows\n"
        ),
        "explanation": (
            "The outer loop runs once per row; for each row, the inner "
            "loop runs all the way through the columns before the outer "
            "loop moves on - so the inner loop's full range repeats once "
            "per outer iteration."
        ),
        "concepts": ["nested loops", "for", "list", "append"],
        "skills": ["iteration", "basic_data_manipulation"],
        "prerequisites": ["loop-007", "loop-008", "loop-009"],
        "track": "python",
        "source": "progressive_python",
    },
    {
        "id": "prog-nested-loop-002",
        "module": "for_loops",
        "difficulty": 4,
        "title": "Flatten a grid (nested loops + accumulator)",
        "description": (
            "Write a function `flatten(grid)` that takes a list of lists "
            "(a grid) and returns a single flat list containing every "
            "element, in row-major order (row by row, left to right)."
        ),
        "examples": "flatten([[1, 2], [3, 4], [5]]) -> [1, 2, 3, 4, 5]",
        "starter_code": "def flatten(grid):\n    # write your code here\n    pass\n",
        "hints": [
            "This combines two patterns you already know: the "
            "accumulator (building a result list) and nested loops "
            "(visiting a grid row by row).",
            "For each row in the grid, loop over that row's elements and "
            "append each one to the result.",
            "result = []\nfor row in grid:\n    for item in row:\n"
            "        result.append(item)\nreturn result",
        ],
        "expected_behavior": "Returns a single flat list with every grid element in order.",
        "hidden_tests": [
            {"call": "flatten([[1, 2], [3, 4], [5]])", "expected": "[1, 2, 3, 4, 5]"},
            {"call": "flatten([[]])", "expected": "[]"},
            {"call": "flatten([])", "expected": "[]"},
        ],
        "solution": (
            "def flatten(grid):\n"
            "    result = []\n"
            "    for row in grid:\n"
            "        for item in row:\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
        "explanation": (
            "The outer loop visits each row; the inner loop visits each "
            "item within that row, appending straight into the shared "
            "result list rather than building a separate list per row."
        ),
        "concepts": ["nested loops", "for", "accumulator", "list"],
        "skills": ["iteration", "basic_data_manipulation"],
        "prerequisites": ["prog-nested-loop-001"],
        "track": "python",
        "source": "progressive_python",
    },
]

DAYS30_EXERCISES: list[dict] = [
    {
        "id": "30days-triangle-area",
        "module": "input_and_formulas",
        "difficulty": 2,
        "title": "Triangle area from user input",
        "description": (
            "Write a script that asks the user for a triangle's base and "
            "height (as two separate prompts) and prints its area, using "
            "the formula area = 0.5 * base * height."
        ),
        "examples": (
            "Enter base: 20\n"
            "Enter height: 10\n"
            "The area of the triangle is 100.0"
        ),
        "starter_code": "# your code here\n",
        "hints": [
            "input() always returns a string - you'll need to convert it "
            "to a number before doing arithmetic with it.",
            "Two separate input() calls, one for each prompt, in the "
            "order the example shows.",
            "base = float(input('Enter base: '))\nheight = float(input("
            "'Enter height: '))\nprint(f'The area of the triangle is "
            "{0.5 * base * height}')",
        ],
        "expected_behavior": "Prints the triangle's area after reading base and height.",
        "hidden_tests": [
            {
                "args": [],
                "stdin": "20\n10\n",
                "expected_stdout": (
                    "Enter base: Enter height: The area of the triangle "
                    "is 100.0"
                ),
                "label": "base 20, height 10",
            },
            {
                "args": [],
                "stdin": "5\n4\n",
                "expected_stdout": (
                    "Enter base: Enter height: The area of the triangle "
                    "is 10.0"
                ),
                "label": "base 5, height 4",
            },
        ],
        "solution": (
            "def main():\n"
            "    base = float(input('Enter base: '))\n"
            "    height = float(input('Enter height: '))\n"
            "    area = 0.5 * base * height\n"
            "    print(f'The area of the triangle is {area}')\n\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        ),
        "explanation": (
            "input() blocks for a line of text and returns it as a "
            "string, so float() converts it to a number before it's used "
            "in the area formula."
        ),
        "concepts": ["input", "float", "formulas"],
        "skills": ["basic_data_manipulation"],
        "exercise_type": "script",
        "track": "python",
        "source": "30_days_of_python",
        "resources": ["python/30-days/03_day_operators.md"],
    },
    {
        "id": "30days-weekly-earning",
        "module": "input_and_formulas",
        "difficulty": 2,
        "title": "Weekly earning from hours and rate",
        "description": (
            "Write a script that asks the user for hours worked and rate "
            "per hour (as two separate prompts) and prints the weekly "
            "earning (hours * rate)."
        ),
        "examples": (
            "Enter hours: 40\n"
            "Enter rate per hour: 28\n"
            "Your weekly earning is 1120.0"
        ),
        "starter_code": "# your code here\n",
        "hints": [
            "Same shape as the triangle-area exercise: two prompts, then "
            "one calculation from both values.",
            "Weekly earning is simply hours multiplied by the hourly "
            "rate.",
            "hours = float(input('Enter hours: '))\nrate = float(input("
            "'Enter rate per hour: '))\nprint(f'Your weekly earning is "
            "{hours * rate}')",
        ],
        "expected_behavior": "Prints the weekly earning after reading hours and rate.",
        "hidden_tests": [
            {
                "args": [],
                "stdin": "40\n28\n",
                "expected_stdout": (
                    "Enter hours: Enter rate per hour: Your weekly "
                    "earning is 1120.0"
                ),
                "label": "40 hours at 28/hr",
            },
            {
                "args": [],
                "stdin": "10\n15\n",
                "expected_stdout": (
                    "Enter hours: Enter rate per hour: Your weekly "
                    "earning is 150.0"
                ),
                "label": "10 hours at 15/hr",
            },
        ],
        "solution": (
            "def main():\n"
            "    hours = float(input('Enter hours: '))\n"
            "    rate = float(input('Enter rate per hour: '))\n"
            "    print(f'Your weekly earning is {hours * rate}')\n\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        ),
        "explanation": (
            "A direct multiplication of the two converted inputs gives "
            "the weekly earning - no loop or condition needed, just "
            "reading input and doing the arithmetic."
        ),
        "concepts": ["input", "float", "formulas"],
        "skills": ["basic_data_manipulation"],
        "exercise_type": "script",
        "track": "python",
        "source": "30_days_of_python",
        "resources": ["python/30-days/03_day_operators.md"],
    },
]


def main() -> None:
    _write(ROOT / "exercises" / "progressive_python", PROGRESSIVE_EXERCISES)
    _write(ROOT / "exercises" / "30_days_of_python", DAYS30_EXERCISES)
    print(
        f"\nTotal: {len(PROGRESSIVE_EXERCISES)} progressive_python, "
        f"{len(DAYS30_EXERCISES)} 30_days_of_python"
    )


if __name__ == "__main__":
    main()
