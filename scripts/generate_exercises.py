"""Generates the Sprint 1 exercise JSON files under exercises/.

Run once with: uv run python scripts/generate_exercises.py
(or plain `python3 scripts/generate_exercises.py` — no dependencies).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"

EXERCISES: list[dict] = [
    # ---------------------------------------------------------------
    # Module: conditions (5 exercises)
    # ---------------------------------------------------------------
    {
        "id": "cond-001",
        "module": "conditions",
        "difficulty": 1,
        "title": "Positive, negative or zero",
        "description": (
            "Write a function `classify_number(n)` that returns the string "
            '"positive", "negative" or "zero" depending on the value of `n`.'
        ),
        "examples": (
            'classify_number(5) -> "positive"\n'
            'classify_number(-3) -> "negative"\n'
            'classify_number(0) -> "zero"'
        ),
        "starter_code": "def classify_number(n):\n    # write your code here\n    pass\n",
        "hints": [
            "You need to compare `n` against zero using comparison operators.",
            "Use if / elif / else: first check n > 0, then n < 0, then the "
            "remaining case.",
            'if n > 0:\n    return "positive"\nelif n < 0:\n    return "negative"'
            '\nelse:\n    return "zero"',
        ],
        "expected_behavior": (
            'Returns exactly one of "positive", "negative", "zero" as a string.'
        ),
        "hidden_tests": [
            {"call": "classify_number(5)", "expected": "'positive'"},
            {"call": "classify_number(-1)", "expected": "'negative'"},
            {"call": "classify_number(0)", "expected": "'zero'"},
            {"call": "classify_number(100)", "expected": "'positive'"},
        ],
        "solution": (
            "def classify_number(n):\n"
            "    if n > 0:\n"
            '        return "positive"\n'
            "    elif n < 0:\n"
            '        return "negative"\n'
            "    else:\n"
            '        return "zero"\n'
        ),
        "explanation": (
            "We compare n against 0 with if/elif/else. Only one branch runs, "
            "and else covers the remaining case (n == 0) without needing an "
            "explicit comparison."
        ),
        "concepts": ["if", "elif", "else", "comparisons"],
    },
    {
        "id": "cond-002",
        "module": "conditions",
        "difficulty": 1,
        "title": "Can this person vote?",
        "description": (
            "Write a function `can_vote(age)` that returns True if `age` is "
            "18 or older, and False otherwise."
        ),
        "examples": "can_vote(20) -> True\ncan_vote(15) -> False\ncan_vote(18) -> True",
        "starter_code": "def can_vote(age):\n    # write your code here\n    pass\n",
        "hints": [
            "This only needs a single comparison, no elif required.",
            "Think about which comparison operator means 'greater than or "
            "equal to'.",
            "if age >= 18:\n    return True\nelse:\n    return False\n\n"
            "(or simply: return age >= 18)",
        ],
        "expected_behavior": "Returns a boolean (True or False).",
        "hidden_tests": [
            {"call": "can_vote(20)", "expected": "True"},
            {"call": "can_vote(17)", "expected": "False"},
            {"call": "can_vote(18)", "expected": "True"},
            {"call": "can_vote(0)", "expected": "False"},
        ],
        "solution": "def can_vote(age):\n    return age >= 18\n",
        "explanation": (
            "A comparison expression like `age >= 18` already evaluates to "
            "True or False, so it can be returned directly without an "
            "if/else block."
        ),
        "concepts": ["if", "comparisons", "bool"],
    },
    {
        "id": "cond-003",
        "module": "conditions",
        "difficulty": 2,
        "title": "The largest of three numbers",
        "description": (
            "Write a function `largest(a, b, c)` that returns the largest "
            "of the three numbers."
        ),
        "examples": "largest(3, 7, 2) -> 7\nlargest(-1, -5, -2) -> -1",
        "starter_code": "def largest(a, b, c):\n    # write your code here\n    pass\n",
        "hints": [
            "You could compare pairs step by step, or look for a Python "
            "built-in that already does this.",
            "Python has a built-in function that returns the largest of "
            "several values.",
            "return max(a, b, c)",
        ],
        "expected_behavior": "Returns the largest of the three arguments.",
        "hidden_tests": [
            {"call": "largest(3, 7, 2)", "expected": "7"},
            {"call": "largest(-1, -5, -2)", "expected": "-1"},
            {"call": "largest(5, 5, 5)", "expected": "5"},
            {"call": "largest(10, 2, 8)", "expected": "10"},
        ],
        "solution": "def largest(a, b, c):\n    return max(a, b, c)\n",
        "explanation": (
            "Python's built-in max() already implements 'find the largest' "
            "for any number of arguments, so we don't need to write the "
            "comparisons by hand."
        ),
        "concepts": ["if", "comparisons", "built-in functions"],
    },
    {
        "id": "cond-004",
        "module": "conditions",
        "difficulty": 2,
        "title": "Divisible by 3 and 5",
        "description": (
            "Write a function `divisible_by_3_and_5(n)` that returns True if "
            "`n` is divisible by both 3 and 5, and False otherwise."
        ),
        "examples": (
            "divisible_by_3_and_5(15) -> True\n"
            "divisible_by_3_and_5(9) -> False\n"
            "divisible_by_3_and_5(10) -> False"
        ),
        "starter_code": (
            "def divisible_by_3_and_5(n):\n    # write your code here\n    pass\n"
        ),
        "hints": [
            "The modulo operator `%` gives you the remainder of a division.",
            "A number is divisible by X when `n % X == 0`. You need both "
            "conditions to be true.",
            "return n % 3 == 0 and n % 5 == 0",
        ],
        "expected_behavior": "Returns a boolean.",
        "hidden_tests": [
            {"call": "divisible_by_3_and_5(15)", "expected": "True"},
            {"call": "divisible_by_3_and_5(9)", "expected": "False"},
            {"call": "divisible_by_3_and_5(10)", "expected": "False"},
            {"call": "divisible_by_3_and_5(0)", "expected": "True"},
        ],
        "solution": (
            "def divisible_by_3_and_5(n):\n    return n % 3 == 0 and n % 5 == 0\n"
        ),
        "explanation": (
            "`%` returns the remainder of a division. A remainder of 0 means "
            "the number divides evenly. `and` combines both conditions so "
            "both must hold."
        ),
        "concepts": ["if", "and", "modulo"],
    },
    {
        "id": "cond-005",
        "module": "conditions",
        "difficulty": 3,
        "title": "Simple grade classifier",
        "description": (
            "Write a function `letter_grade(score)` that converts a numeric "
            "score (0-100) into a letter grade:\n"
            "90+  -> 'A'\n80-89 -> 'B'\n70-79 -> 'C'\n60-69 -> 'D'\n"
            "below 60 -> 'F'"
        ),
        "examples": (
            "letter_grade(95) -> 'A'\nletter_grade(82) -> 'B'\n"
            "letter_grade(40) -> 'F'"
        ),
        "starter_code": "def letter_grade(score):\n    # write your code here\n    pass\n",
        "hints": [
            "You'll need a chain of elif branches, checked from highest to "
            "lowest.",
            "Order matters: check `score >= 90` first, so a 95 doesn't "
            "accidentally match a lower branch.",
            "if score >= 90:\n    return 'A'\nelif score >= 80:\n    return 'B'"
            "\nelif score >= 70:\n    return 'C'\nelif score >= 60:\n    "
            "return 'D'\nelse:\n    return 'F'",
        ],
        "expected_behavior": "Returns one of 'A', 'B', 'C', 'D', 'F'.",
        "hidden_tests": [
            {"call": "letter_grade(95)", "expected": "'A'"},
            {"call": "letter_grade(82)", "expected": "'B'"},
            {"call": "letter_grade(75)", "expected": "'C'"},
            {"call": "letter_grade(61)", "expected": "'D'"},
            {"call": "letter_grade(40)", "expected": "'F'"},
        ],
        "solution": (
            "def letter_grade(score):\n"
            "    if score >= 90:\n        return 'A'\n"
            "    elif score >= 80:\n        return 'B'\n"
            "    elif score >= 70:\n        return 'C'\n"
            "    elif score >= 60:\n        return 'D'\n"
            "    else:\n        return 'F'\n"
        ),
        "explanation": (
            "elif chains are evaluated top to bottom, and the first true "
            "condition wins. Checking from highest to lowest means once "
            "we pass the 90 check, we know score < 90 for every branch below."
        ),
        "concepts": ["if", "elif", "else", "comparisons"],
    },
    # ---------------------------------------------------------------
    # Module: for_loops (10 exercises, following the level structure)
    # ---------------------------------------------------------------
    {
        "id": "loop-001",
        "module": "for_loops",
        "difficulty": 1,
        "title": "Read a loop (trace the output)",
        "description": (
            "Look at this code:\n\n"
            "numbers = [1, 2, 3]\n"
            "for number in numbers:\n"
            "    print(number)\n\n"
            "Write a function `trace_output()` that returns a LIST of the "
            "lines that would be printed, as strings, in order. "
            "(This exercise trains reading loops, not writing them.)"
        ),
        "examples": "trace_output() -> ['1', '2', '3']",
        "starter_code": "def trace_output():\n    # write your code here\n    pass\n",
        "hints": [
            "You don't need a loop to answer this — you need to mentally "
            "run the one shown above and write down what happens.",
            "Each `print(number)` produces one line. What are the three "
            "values `number` takes?",
            "return ['1', '2', '3']",
        ],
        "expected_behavior": "Returns a list of 3 strings: ['1', '2', '3'].",
        "hidden_tests": [
            {"call": "trace_output()", "expected": "['1', '2', '3']"},
        ],
        "solution": "def trace_output():\n    return ['1', '2', '3']\n",
        "explanation": (
            "`for number in numbers` visits each element of the list in "
            "order, binding it to `number`, then runs the loop body once "
            "per element — so `print(number)` runs 3 times, once per item."
        ),
        "concepts": ["for", "list", "reading code"],
    },
    {
        "id": "loop-002",
        "module": "for_loops",
        "difficulty": 1,
        "title": "Print every number",
        "description": (
            "Write a function `print_all(numbers)` that prints every number "
            "in the list `numbers`, one per line, and also returns None "
            "(this exercise is about the loop, not the return value)."
        ),
        "examples": "print_all([1, 2, 3, 4, 5]) prints:\n1\n2\n3\n4\n5",
        "starter_code": "def print_all(numbers):\n    # write your code here\n    pass\n",
        "hints": [
            "You need a `for` loop that goes through every item in `numbers`.",
            "Inside the loop body, call print() on the current item.",
            "for number in numbers:\n    print(number)",
        ],
        "expected_behavior": "Prints each number on its own line, nothing else.",
        "hidden_tests": [
            {"call": "print_all([1, 2, 3])", "expected": "None"},
            {"call": "print_all([])", "expected": "None"},
        ],
        "solution": "def print_all(numbers):\n    for number in numbers:\n        print(number)\n",
        "explanation": (
            "A `for` loop repeats its body once per item in the list, "
            "automatically stopping when it reaches the end — no manual "
            "counting required."
        ),
        "concepts": ["for", "list", "print"],
    },
    {
        "id": "loop-003",
        "module": "for_loops",
        "difficulty": 2,
        "title": "Sum the numbers (accumulator)",
        "description": (
            "Write a function `sum_numbers(numbers)` that returns the sum "
            "of all numbers in the list, using a loop (not the built-in "
            "`sum()`)."
        ),
        "examples": "sum_numbers([4, 7, 2, 9]) -> 22",
        "starter_code": "def sum_numbers(numbers):\n    # write your code here\n    pass\n",
        "hints": [
            "What information do you need to keep while iterating?",
            "You probably need a variable that starts at 0 and stores the "
            "running total.",
            "total = 0\nfor number in numbers:\n    total = total + number\n"
            "return total",
        ],
        "expected_behavior": "Returns the sum as an int or float.",
        "hidden_tests": [
            {"call": "sum_numbers([4, 7, 2, 9])", "expected": "22"},
            {"call": "sum_numbers([])", "expected": "0"},
            {"call": "sum_numbers([-1, 1])", "expected": "0"},
            {"call": "sum_numbers([10])", "expected": "10"},
        ],
        "solution": (
            "def sum_numbers(numbers):\n"
            "    total = 0\n"
            "    for number in numbers:\n"
            "        total = total + number\n"
            "    return total\n"
        ),
        "explanation": (
            "This is the accumulator pattern: start a variable at a neutral "
            "value (0 for a sum), then update it once per loop iteration. "
            "By the time the loop ends, it holds the combined result."
        ),
        "concepts": ["for", "list", "accumulator"],
    },
    {
        "id": "loop-004",
        "module": "for_loops",
        "difficulty": 2,
        "title": "Multiply everything (accumulator)",
        "description": (
            "Write a function `product(numbers)` that returns the product "
            "of all numbers in the list using a loop."
        ),
        "examples": "product([1, 2, 3, 4]) -> 24",
        "starter_code": "def product(numbers):\n    # write your code here\n    pass\n",
        "hints": [
            "This is the same accumulator pattern as summing, but with a "
            "different operation.",
            "What starting value keeps a product unchanged when you "
            "multiply by it?",
            "result = 1\nfor number in numbers:\n    result = result * number\n"
            "return result",
        ],
        "expected_behavior": "Returns the product as an int or float.",
        "hidden_tests": [
            {"call": "product([1, 2, 3, 4])", "expected": "24"},
            {"call": "product([5])", "expected": "5"},
            {"call": "product([2, 0, 3])", "expected": "0"},
        ],
        "solution": (
            "def product(numbers):\n"
            "    result = 1\n"
            "    for number in numbers:\n"
            "        result = result * number\n"
            "    return result\n"
        ),
        "explanation": (
            "The accumulator starts at 1 (the multiplicative identity) "
            "instead of 0, because multiplying by 0 would zero everything "
            "out immediately."
        ),
        "concepts": ["for", "list", "accumulator"],
    },
    {
        "id": "loop-005",
        "module": "for_loops",
        "difficulty": 2,
        "title": "Count even numbers",
        "description": (
            "Write a function `count_even(numbers)` that returns how many "
            "numbers in the list are even."
        ),
        "examples": "count_even([1, 2, 3, 4, 5, 6]) -> 3",
        "starter_code": "def count_even(numbers):\n    # write your code here\n    pass\n",
        "hints": [
            "A counter is an accumulator that only increases when a "
            "condition is true.",
            "Start a counter at 0, and inside the loop, check "
            "`number % 2 == 0` before incrementing it.",
            "count = 0\nfor number in numbers:\n    if number % 2 == 0:\n"
            "        count = count + 1\nreturn count",
        ],
        "expected_behavior": "Returns an integer count.",
        "hidden_tests": [
            {"call": "count_even([1, 2, 3, 4, 5, 6])", "expected": "3"},
            {"call": "count_even([1, 3, 5])", "expected": "0"},
            {"call": "count_even([])", "expected": "0"},
            {"call": "count_even([2, 4, 6])", "expected": "3"},
        ],
        "solution": (
            "def count_even(numbers):\n"
            "    count = 0\n"
            "    for number in numbers:\n"
            "        if number % 2 == 0:\n"
            "            count = count + 1\n"
            "    return count\n"
        ),
        "explanation": (
            "A counter combines the accumulator pattern with a condition: "
            "the running total only changes when the `if` is true, so it "
            "ends up counting matching items instead of summing values."
        ),
        "concepts": ["for", "if", "counter"],
    },
    {
        "id": "loop-006",
        "module": "for_loops",
        "difficulty": 2,
        "title": "Count the vowels",
        "description": (
            "Write a function `count_vowels(text)` that returns how many "
            "characters in `text` are vowels (a, e, i, o, u — lowercase "
            "only, you can assume the input is already lowercase)."
        ),
        "examples": "count_vowels('hello world') -> 3",
        "starter_code": "def count_vowels(text):\n    # write your code here\n    pass\n",
        "hints": [
            "Strings can be looped over directly, character by character.",
            "Keep a counter, and check membership: is the current "
            "character one of 'aeiou'?",
            "count = 0\nfor char in text:\n    if char in 'aeiou':\n"
            "        count = count + 1\nreturn count",
        ],
        "expected_behavior": "Returns an integer count of vowels.",
        "hidden_tests": [
            {"call": "count_vowels('hello world')", "expected": "3"},
            {"call": "count_vowels('xyz')", "expected": "0"},
            {"call": "count_vowels('aeiou')", "expected": "5"},
            {"call": "count_vowels('')", "expected": "0"},
        ],
        "solution": (
            "def count_vowels(text):\n"
            "    count = 0\n"
            "    for char in text:\n"
            "        if char in 'aeiou':\n"
            "            count = count + 1\n"
            "    return count\n"
        ),
        "explanation": (
            "A `for` loop over a string yields one character at a time. "
            "The `in` operator checks membership in the vowel string, so "
            "the counter only increases for matching characters."
        ),
        "concepts": ["for", "if", "string iteration", "counter"],
    },
    {
        "id": "loop-007",
        "module": "for_loops",
        "difficulty": 3,
        "title": "Filter numbers greater than 5",
        "description": (
            "Write a function `filter_greater_than_5(numbers)` that returns "
            "a NEW list containing only the numbers greater than 5."
        ),
        "examples": "filter_greater_than_5([1, 5, 8, 2, 10, 3]) -> [8, 10]",
        "starter_code": (
            "def filter_greater_than_5(numbers):\n    # write your code here\n"
            "    pass\n"
        ),
        "hints": [
            "This time the accumulator isn't a number, it's a list you "
            "build up.",
            "Start with an empty list, and use `.append()` when a number "
            "passes the condition.",
            "result = []\nfor number in numbers:\n    if number > 5:\n"
            "        result.append(number)\nreturn result",
        ],
        "expected_behavior": "Returns a new list, preserving the original order.",
        "hidden_tests": [
            {
                "call": "filter_greater_than_5([1, 5, 8, 2, 10, 3])",
                "expected": "[8, 10]",
            },
            {"call": "filter_greater_than_5([1, 2, 3])", "expected": "[]"},
            {"call": "filter_greater_than_5([])", "expected": "[]"},
        ],
        "solution": (
            "def filter_greater_than_5(numbers):\n"
            "    result = []\n"
            "    for number in numbers:\n"
            "        if number > 5:\n"
            "            result.append(number)\n"
            "    return result\n"
        ),
        "explanation": (
            "Filtering is the list version of the accumulator pattern: "
            "instead of updating a single number, we grow a list, adding "
            "only the elements that satisfy the condition."
        ),
        "concepts": ["for", "if", "list", "append", "filtering"],
    },
    {
        "id": "loop-008",
        "module": "for_loops",
        "difficulty": 3,
        "title": "Double every number (transformation)",
        "description": (
            "Write a function `double_all(numbers)` that returns a NEW list "
            "where every number has been multiplied by 2."
        ),
        "examples": "double_all([1, 2, 3, 4]) -> [2, 4, 6, 8]",
        "starter_code": "def double_all(numbers):\n    # write your code here\n    pass\n",
        "hints": [
            "Similar to filtering, but every element is transformed and "
            "kept, none are skipped.",
            "Build a new list, and append `number * 2` for each item.",
            "result = []\nfor number in numbers:\n    result.append(number * 2)"
            "\nreturn result",
        ],
        "expected_behavior": "Returns a new list, same length as the input.",
        "hidden_tests": [
            {"call": "double_all([1, 2, 3, 4])", "expected": "[2, 4, 6, 8]"},
            {"call": "double_all([])", "expected": "[]"},
            {"call": "double_all([0, -1])", "expected": "[0, -2]"},
        ],
        "solution": (
            "def double_all(numbers):\n"
            "    result = []\n"
            "    for number in numbers:\n"
            "        result.append(number * 2)\n"
            "    return result\n"
        ),
        "explanation": (
            "A transformation loop appends a modified version of every "
            "item, unlike filtering which appends only some items "
            "unchanged."
        ),
        "concepts": ["for", "list", "append", "transformation"],
    },
    {
        "id": "loop-009",
        "module": "for_loops",
        "difficulty": 3,
        "title": "Numbered list with enumerate",
        "description": (
            "Write a function `numbered_lines(items)` that returns a list "
            "of strings formatted as '<index> <item>', starting at index 0."
        ),
        "examples": (
            "numbered_lines(['apple', 'banana', 'orange']) -> "
            "['0 apple', '1 banana', '2 orange']"
        ),
        "starter_code": "def numbered_lines(items):\n    # write your code here\n    pass\n",
        "hints": [
            "You need both the position and the value of each item while "
            "looping — a plain `for item in items` only gives you the "
            "value.",
            "`enumerate(items)` gives you (index, item) pairs you can "
            "unpack directly in the for line.",
            "result = []\nfor index, item in enumerate(items):\n"
            '    result.append(f"{index} {item}")\nreturn result',
        ],
        "expected_behavior": "Returns a list of formatted strings, one per item.",
        "hidden_tests": [
            {
                "call": "numbered_lines(['apple', 'banana', 'orange'])",
                "expected": "['0 apple', '1 banana', '2 orange']",
            },
            {"call": "numbered_lines([])", "expected": "[]"},
            {"call": "numbered_lines(['x'])", "expected": "['0 x']"},
        ],
        "solution": (
            "def numbered_lines(items):\n"
            "    result = []\n"
            "    for index, item in enumerate(items):\n"
            '        result.append(f"{index} {item}")\n'
            "    return result\n"
        ),
        "explanation": (
            "`enumerate()` wraps an iterable and yields (index, value) "
            "tuples, which we unpack directly into `index, item` in the "
            "for line — avoiding a manually managed counter variable."
        ),
        "concepts": ["for", "enumerate", "f-strings", "list"],
    },
    {
        "id": "loop-010",
        "module": "for_loops",
        "difficulty": 4,
        "title": "Average of positive numbers",
        "description": (
            "Write a function `average_of_positives(numbers)` that returns "
            "the average of only the POSITIVE numbers in the list. If there "
            "are no positive numbers, return 0."
        ),
        "examples": (
            "average_of_positives([1, -2, 3, -4, 5]) -> 3.0\n"
            "average_of_positives([-1, -2]) -> 0"
        ),
        "starter_code": (
            "def average_of_positives(numbers):\n    # write your code here\n"
            "    pass\n"
        ),
        "hints": [
            "You need two things at once while looping: a running total, "
            "and a count of how many numbers were actually included.",
            "Only update the total and the count when a number is > 0. "
            "Watch out for dividing by zero when there are no positives.",
            "total = 0\ncount = 0\nfor number in numbers:\n"
            "    if number > 0:\n        total = total + number\n"
            "        count = count + 1\nif count == 0:\n    return 0\n"
            "return total / count",
        ],
        "expected_behavior": (
            "Returns a number (int or float). Returns 0 when there are no "
            "positive numbers, to avoid dividing by zero."
        ),
        "hidden_tests": [
            {
                "call": "average_of_positives([1, -2, 3, -4, 5])",
                "expected": "3.0",
            },
            {"call": "average_of_positives([-1, -2])", "expected": "0"},
            {"call": "average_of_positives([2, 4, 6])", "expected": "4.0"},
        ],
        "solution": (
            "def average_of_positives(numbers):\n"
            "    total = 0\n"
            "    count = 0\n"
            "    for number in numbers:\n"
            "        if number > 0:\n"
            "            total = total + number\n"
            "            count = count + 1\n"
            "    if count == 0:\n"
            "        return 0\n"
            "    return total / count\n"
        ),
        "explanation": (
            "This combines two accumulators (a sum and a counter) guarded "
            "by the same condition, then divides at the very end — after "
            "the loop, not inside it — and guards against dividing by zero."
        ),
        "concepts": ["for", "if", "accumulator", "counter", "division"],
    },
    # ---------------------------------------------------------------
    # Module: lists (5 exercises)
    # ---------------------------------------------------------------
    {
        "id": "list-001",
        "module": "lists",
        "difficulty": 1,
        "title": "First and last element",
        "description": (
            "Write a function `first_and_last(items)` that returns a tuple "
            "with the first and last element of the list `items`. You can "
            "assume the list has at least one element."
        ),
        "examples": "first_and_last([1, 2, 3, 4]) -> (1, 4)",
        "starter_code": "def first_and_last(items):\n    # write your code here\n    pass\n",
        "hints": [
            "Lists support indexing with square brackets, and negative "
            "indices count from the end.",
            "`items[0]` is the first element. What index gives you the "
            "last one without knowing the length?",
            "return (items[0], items[-1])",
        ],
        "expected_behavior": "Returns a tuple of (first_element, last_element).",
        "hidden_tests": [
            {"call": "first_and_last([1, 2, 3, 4])", "expected": "(1, 4)"},
            {"call": "first_and_last([5])", "expected": "(5, 5)"},
            {"call": "first_and_last(['a', 'b', 'c'])", "expected": "('a', 'c')"},
        ],
        "solution": "def first_and_last(items):\n    return (items[0], items[-1])\n",
        "explanation": (
            "Index 0 always refers to the first element. Index -1 refers "
            "to the last element regardless of the list's length, which "
            "avoids needing `len(items) - 1`."
        ),
        "concepts": ["list", "indexing", "negative indexing"],
    },
    {
        "id": "list-002",
        "module": "lists",
        "difficulty": 1,
        "title": "Middle slice",
        "description": (
            "Write a function `middle(items)` that returns every element "
            "except the first and the last, as a list."
        ),
        "examples": "middle([1, 2, 3, 4, 5]) -> [2, 3, 4]",
        "starter_code": "def middle(items):\n    # write your code here\n    pass\n",
        "hints": [
            "Slicing lets you take a range of a list using `items[start:end]`.",
            "Start at index 1 (skip the first) and stop at index -1 "
            "(exclude the last).",
            "return items[1:-1]",
        ],
        "expected_behavior": "Returns a new list without its first and last elements.",
        "hidden_tests": [
            {"call": "middle([1, 2, 3, 4, 5])", "expected": "[2, 3, 4]"},
            {"call": "middle([1, 2])", "expected": "[]"},
            {"call": "middle([1, 2, 3])", "expected": "[2]"},
        ],
        "solution": "def middle(items):\n    return items[1:-1]\n",
        "explanation": (
            "Slicing `items[1:-1]` starts right after the first element "
            "and stops right before the last one, since slice ends are "
            "exclusive."
        ),
        "concepts": ["list", "slicing"],
    },
    {
        "id": "list-003",
        "module": "lists",
        "difficulty": 2,
        "title": "Remove duplicates, keep order",
        "description": (
            "Write a function `remove_duplicates(items)` that returns a new "
            "list with duplicate values removed, keeping the first "
            "occurrence of each value and preserving order."
        ),
        "examples": "remove_duplicates([1, 2, 2, 3, 1, 4]) -> [1, 2, 3, 4]",
        "starter_code": (
            "def remove_duplicates(items):\n    # write your code here\n    pass\n"
        ),
        "hints": [
            "You'll need to remember which values you've already added, "
            "so you can decide whether to skip a repeat.",
            "Keep a result list and a 'seen' list (or membership check "
            "against the result itself) — only append when the value "
            "hasn't been added yet.",
            "result = []\nfor item in items:\n    if item not in result:\n"
            "        result.append(item)\nreturn result",
        ],
        "expected_behavior": "Returns a new list with only the first occurrence of each value.",
        "hidden_tests": [
            {
                "call": "remove_duplicates([1, 2, 2, 3, 1, 4])",
                "expected": "[1, 2, 3, 4]",
            },
            {"call": "remove_duplicates([])", "expected": "[]"},
            {"call": "remove_duplicates([1, 1, 1])", "expected": "[1]"},
        ],
        "solution": (
            "def remove_duplicates(items):\n"
            "    result = []\n"
            "    for item in items:\n"
            "        if item not in result:\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
        "explanation": (
            "`item not in result` checks whether the value has already "
            "been added. Because we check before appending, only the "
            "first occurrence of each value ends up in the result."
        ),
        "concepts": ["for", "if", "list", "membership", "append"],
    },
    {
        "id": "list-004",
        "module": "lists",
        "difficulty": 2,
        "title": "Find the index of the maximum",
        "description": (
            "Write a function `index_of_max(numbers)` that returns the "
            "index of the largest number in the list. Assume the list is "
            "not empty, and if there's a tie, return the first index."
        ),
        "examples": "index_of_max([3, 7, 2, 9, 4]) -> 3",
        "starter_code": "def index_of_max(numbers):\n    # write your code here\n    pass\n",
        "hints": [
            "You need to track both the best value seen so far AND its "
            "position, so plain `for number in numbers` isn't quite enough.",
            "Use `enumerate()` to get (index, number) pairs, and update "
            "your 'best so far' variables only when you find something "
            "larger.",
            "best_index = 0\nbest_value = numbers[0]\n"
            "for index, number in enumerate(numbers):\n"
            "    if number > best_value:\n        best_value = number\n"
            "        best_index = index\nreturn best_index",
        ],
        "expected_behavior": "Returns an integer index into the list.",
        "hidden_tests": [
            {"call": "index_of_max([3, 7, 2, 9, 4])", "expected": "3"},
            {"call": "index_of_max([5])", "expected": "0"},
            {"call": "index_of_max([1, 5, 5, 2])", "expected": "1"},
        ],
        "solution": (
            "def index_of_max(numbers):\n"
            "    best_index = 0\n"
            "    best_value = numbers[0]\n"
            "    for index, number in enumerate(numbers):\n"
            "        if number > best_value:\n"
            "            best_value = number\n"
            "            best_index = index\n"
            "    return best_index\n"
        ),
        "explanation": (
            "This is the 'running best' pattern: initialize with the first "
            "element, then only overwrite the tracked best when a strictly "
            "larger value appears — the strict `>` naturally keeps ties on "
            "the earliest index."
        ),
        "concepts": ["for", "enumerate", "if", "list"],
    },
    {
        "id": "list-005",
        "module": "lists",
        "difficulty": 3,
        "title": "Merge two lists, alternating",
        "description": (
            "Write a function `interleave(a, b)` that returns a new list "
            "alternating elements from `a` and `b`, starting with `a`. "
            "Assume both lists have the same length."
        ),
        "examples": "interleave([1, 3, 5], [2, 4, 6]) -> [1, 2, 3, 4, 5, 6]",
        "starter_code": "def interleave(a, b):\n    # write your code here\n    pass\n",
        "hints": [
            "You're walking through both lists at the same position at "
            "the same time, so you'll need the index, not just the values.",
            "Loop using `enumerate(a)` (or `range(len(a))`), and for each "
            "index append both `a[index]` and `b[index]`.",
            "result = []\nfor index, value in enumerate(a):\n"
            "    result.append(value)\n    result.append(b[index])\n"
            "return result",
        ],
        "expected_behavior": "Returns a list twice the length of the inputs, alternating a/b.",
        "hidden_tests": [
            {
                "call": "interleave([1, 3, 5], [2, 4, 6])",
                "expected": "[1, 2, 3, 4, 5, 6]",
            },
            {"call": "interleave([], [])", "expected": "[]"},
            {"call": "interleave(['a'], ['b'])", "expected": "['a', 'b']"},
        ],
        "solution": (
            "def interleave(a, b):\n"
            "    result = []\n"
            "    for index, value in enumerate(a):\n"
            "        result.append(value)\n"
            "        result.append(b[index])\n"
            "    return result\n"
        ),
        "explanation": (
            "`enumerate(a)` gives us the index we need to reach into `b` "
            "at the same position, so each loop iteration appends one "
            "element from each list, in a-then-b order."
        ),
        "concepts": ["for", "enumerate", "list", "indexing"],
    },
]


def main() -> None:
    for exercise in EXERCISES:
        module_dir = EXERCISES_DIR / exercise["module"]
        module_dir.mkdir(parents=True, exist_ok=True)
        out_path = module_dir / f"{exercise['id']}.json"
        out_path.write_text(
            json.dumps(exercise, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out_path.relative_to(ROOT)}")
    print(f"\nTotal exercises: {len(EXERCISES)}")


if __name__ == "__main__":
    main()
