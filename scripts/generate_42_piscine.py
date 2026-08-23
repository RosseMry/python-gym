"""Generates exercise JSON files for the 42 Python Piscine content source.

Sourced directly from the PDF subjects the user provided (Training
Piscine Python for Data Science - 0, 3, 4). Per Sprint 2 spec section
40 ("no inventar contenido"), statements, constraints and examples are
kept faithful to those PDFs. Not every exercise in those PDFs can be
auto-graded with the current engine (e.g. exercises whose output
depends on the current date, or ones needing a real terminal/timing
behaviour like ft_tqdm) - those are still included with full metadata
so they show up in the learning path, just with `hidden_tests: []`
and a note in `explanation` about manual verification.

Module 1 (Array) and Module 2 (DataTable) of the same Piscine series
require numpy/pandas/PIL and image/dataset files - out of scope for
Sprint 2 (spec section 43 explicitly excludes NumPy/Pandas this
sprint). They are deliberately not included here; see the Sprint 2
review notes for that decision.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises" / "42_python_piscine"

COMMON = {
    "source": "42_python_piscine",
    "track": "python",
    "validation_profile": "42_piscine",
}

EXERCISES: list[dict] = [
    # ---------------------------------------------------------------
    # Module 0 - Starting (en_subject.pdf)
    # ---------------------------------------------------------------
    {
        "id": "piscine-00-hello",
        "module": "piscine_00_starting",
        "difficulty": 1,
        "title": "First python script (Hello)",
        "description": (
            "You need to modify the string of each data object to display "
            'the following greetings: "Hello World", "Hello «country of '
            'your campus»", "Hello «city of your campus»", "Hello «name of '
            'your campus»".\n\n'
            "Starter data:\n"
            'ft_list = ["Hello", "tata!"]\n'
            'ft_tuple = ("Hello", "toto!")\n'
            'ft_set = {"Hello", "tutu!"}\n'
            'ft_dict = {"Hello" : "titi!"}\n\n'
            "Then print each of the four objects, one per line.\n\n"
            "For this exercise, use the 42 Paris campus as your reference "
            "campus (France / Paris / 42Paris)."
        ),
        "examples": (
            "$> python Hello.py | cat -e\n"
            "['Hello', 'World!']$\n"
            "('Hello', 'France!')$\n"
            "{'Hello', 'Paris!'}$\n"
            "{'Hello': '42Paris!'}$\n$>"
        ),
        "starter_code": (
            'ft_list = ["Hello", "tata!"]\n'
            'ft_tuple = ("Hello", "toto!")\n'
            'ft_set = {"Hello", "tutu!"}\n'
            'ft_dict = {"Hello" : "titi!"}\n\n'
            "# your code here\n\n"
            "print(ft_list)\n"
            "print(ft_tuple)\n"
            "print(ft_set)\n"
            "print(ft_dict)\n"
        ),
        "hints": [
            "You need to replace the second element of the list/tuple, "
            "the second element of the set, and the value of the dict - "
            "not create new objects.",
            "Lists support item assignment by index (ft_list[1] = ...). "
            "Tuples don't - you'll need to rebuild the tuple. Sets don't "
            "support indexing either - remove the old value and add the "
            "new one.",
            'ft_list[1] = "World!"\n'
            'ft_tuple = ("Hello", "France!")\n'
            'ft_set.remove("tutu!")\n'
            'ft_set.add("Paris!")\n'
            'ft_dict["Hello"] = "42Paris!"',
        ],
        "expected_behavior": (
            "Prints the four objects, each showing 'Hello' paired with "
            "World/France/Paris/42Paris."
        ),
        "hidden_tests": [
            {
                "args": [],
                "expected_stdout": (
                    "['Hello', 'World!']\n"
                    "('Hello', 'France!')\n"
                    "{'Hello', 'Paris!'}\n"
                    "{'Hello': '42Paris!'}"
                ),
                "label": "Test 1",
            }
        ],
        "solution": (
            'ft_list = ["Hello", "tata!"]\n'
            'ft_tuple = ("Hello", "toto!")\n'
            'ft_set = {"Hello", "tutu!"}\n'
            'ft_dict = {"Hello" : "titi!"}\n\n'
            'ft_list[1] = "World!"\n'
            'ft_tuple = ("Hello", "France!")\n'
            'ft_set.remove("tutu!")\n'
            'ft_set.add("Paris!")\n'
            'ft_dict["Hello"] = "42Paris!"\n\n'
            "print(ft_list)\n"
            "print(ft_tuple)\n"
            "print(ft_set)\n"
            "print(ft_dict)\n"
        ),
        "explanation": (
            "Lists are mutable and support index assignment. Tuples are "
            "immutable, so a new tuple has to be built. Sets have no "
            "index, so the old value is removed and the new one added. "
            "Dicts are updated by assigning to the existing key."
        ),
        "concepts": ["list", "tuple", "set", "dict", "mutability"],
        "skills": ["basic_data_manipulation"],
        "exercise_type": "script",
        **COMMON,
    },
    {
        "id": "piscine-00-format-time",
        "module": "piscine_00_starting",
        "difficulty": 1,
        "title": "First use of package (format the date)",
        "description": (
            "Write a script that formats the current date two ways: the "
            "number of seconds since January 1, 1970 (with thousands "
            "separators, and again in scientific notation), and the "
            "current date as 'Mon DD YYYY'.\n\n"
            "Allowed: time, datetime, or any other library that gives you "
            "the current date."
        ),
        "examples": (
            "$> python format_ft_time.py | cat -e\n"
            "Seconds since January 1, 1970: 1,666,355,857.3622 or "
            "1.67e+09 in scientific notation$\n"
            "Oct 21 2022$\n$>"
        ),
        "starter_code": "# your code here\n",
        "hints": [
            "time.time() gives you seconds since the epoch as a float.",
            "Format numbers with f-strings: f'{value:,}' adds thousands "
            "separators, f'{value:.2e}' gives scientific notation.",
            "datetime.now().strftime('%b %d %Y') gives 'Oct 21 2022'-style "
            "output.",
        ],
        "expected_behavior": (
            "Prints the seconds-since-epoch line, then the formatted "
            "date. The exact numbers will differ every run - see the "
            "note below."
        ),
        "hidden_tests": [],
        "solution": (
            "import time\n"
            "from datetime import datetime\n\n"
            "now = time.time()\n"
            "print(\n"
            "    f'Seconds since January 1, 1970: {now:,.4f} or '\n"
            "    f'{now:.2e} in scientific notation'\n"
            ")\n"
            "print(datetime.now().strftime('%b %d %Y'))\n"
        ),
        "explanation": (
            "time.time() returns the current Unix timestamp. f-string "
            "format specs handle both the thousands separator and "
            "scientific notation without manual string building."
        ),
        "concepts": ["time", "datetime", "f-strings", "formatting"],
        "skills": ["date_time_handling"],
        "exercise_type": "script",
        **COMMON,
    },
    {
        "id": "piscine-00-find-type",
        "module": "piscine_00_starting",
        "difficulty": 1,
        "title": "First function python (find the type)",
        "description": (
            "Write a function `all_thing_is_obj(object)` that prints the "
            "type of the object it receives, then returns 42.\n\n"
            "For a list, print 'List : <class ...>'. For a tuple, print "
            "'Tuple : <class ...>'. For a set, print 'Set : <class ...>'. "
            "For a dict, print 'Dict : <class ...>'. For any other string, "
            "print '<the string> is in the kitchen : <class ...>'. For any "
            "other type, print 'Type not found'.\n\n"
            "Calling the function directly (without going through a "
            "tester) does nothing by itself - there is no code at the "
            "top level of this file."
        ),
        "examples": (
            "all_thing_is_obj(['Hello', 'tata!'])\n"
            "-> prints \"List : <class 'list'>\"\n\n"
            "all_thing_is_obj('Brian')\n"
            "-> prints \"Brian is in the kitchen : <class 'str'>\"\n\n"
            "print(all_thing_is_obj(10))\n"
            "-> prints \"Type not found\", then 42"
        ),
        "starter_code": (
            "def all_thing_is_obj(object):\n"
            "    # your code here\n"
            "    pass\n"
        ),
        "hints": [
            "Check the object's exact type with type(object) is list, "
            "type(object) is tuple, etc. - order matters since bool is a "
            "subclass of int and str needs its own case.",
            "For the string case, the printed message includes the "
            "string's own value, not a fixed word.",
            "if type(object) is list:\n    print(f\"List : {type(object)}\")"
            "\nelif type(object) is str:\n    print(f\"{object} is in the "
            "kitchen : {type(object)}\")\n...\nelse:\n    "
            'print("Type not found")\nreturn 42',
        ],
        "expected_behavior": "Always returns 42, and prints one line describing the type.",
        "hidden_tests": [
            {"call": "all_thing_is_obj([1, 2])", "expected": "42"},
            {"call": "all_thing_is_obj((1, 2))", "expected": "42"},
            {"call": "all_thing_is_obj({1, 2})", "expected": "42"},
            {"call": "all_thing_is_obj({'a': 1})", "expected": "42"},
            {"call": "all_thing_is_obj('Brian')", "expected": "42"},
            {"call": "all_thing_is_obj(10)", "expected": "42"},
        ],
        "solution": (
            "def all_thing_is_obj(object):\n"
            "    if type(object) is list:\n"
            '        print(f"List : {type(object)}")\n'
            "    elif type(object) is tuple:\n"
            '        print(f"Tuple : {type(object)}")\n'
            "    elif type(object) is set:\n"
            '        print(f"Set : {type(object)}")\n'
            "    elif type(object) is dict:\n"
            '        print(f"Dict : {type(object)}")\n'
            "    elif type(object) is str:\n"
            '        print(f"{object} is in the kitchen : {type(object)}")\n'
            "    else:\n"
            '        print("Type not found")\n'
            "    return 42\n"
        ),
        "explanation": (
            "type(x) is list (rather than isinstance) matches the exact "
            "type only, which matters here since the subject wants a "
            "specific branch per container type."
        ),
        "concepts": ["type", "if/elif", "functions"],
        "skills": ["type_introspection"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-00-null-not-found",
        "module": "piscine_00_starting",
        "difficulty": 1,
        "title": "NULL not found",
        "description": (
            "Write a function `NULL_not_found(object)` that prints the "
            "object's type for every flavour of 'nothing' in Python "
            "(None, NaN, 0, empty string, False), and prints 'Type not "
            "Found' for anything else. Return 0 on success, 1 on error.\n\n"
            "Expected print format: 'Nothing: None <class \\'NoneType\\'>' "
            "style - the value, then its type."
        ),
        "examples": (
            "NULL_not_found(None) -> prints \"None <class 'NoneType'>\"\n"
            "NULL_not_found(float('nan')) -> prints \"nan <class "
            "'float'>\"\n"
            "print(NULL_not_found('Brian')) -> prints \"Type not Found\", "
            "then 1"
        ),
        "starter_code": (
            "def NULL_not_found(object):\n"
            "    # your code here\n"
            "    pass\n"
        ),
        "hints": [
            "None, NaN, 0, '' and False are five distinct 'falsy' values "
            "with five different types - you can't just check `if not "
            "object`, because that would also match values you should "
            "report as 'Type not Found' (like an empty list).",
            "NaN is tricky: `float('nan') == float('nan')` is False. "
            "Checking the exact type (`type(object) is float` combined "
            "with `object != object`) is one reliable way to detect it.",
            "if object is None:\n    ...\nelif type(object) is float and "
            "object != object:\n    ...  # NaN\nelif object is False:\n"
            "    ...\nelif type(object) is int and object == 0:\n    ...\n"
            "elif type(object) is str and object == '':\n    ...\nelse:\n"
            '    print("Type not Found")\n    return 1\nreturn 0',
        ],
        "expected_behavior": "Returns 0 for a recognised 'null' value, 1 otherwise.",
        "hidden_tests": [
            {"call": "NULL_not_found(None)", "expected": "0"},
            {"call": "NULL_not_found(float('nan'))", "expected": "0"},
            {"call": "NULL_not_found(0)", "expected": "0"},
            {"call": "NULL_not_found('')", "expected": "0"},
            {"call": "NULL_not_found(False)", "expected": "0"},
            {"call": "NULL_not_found('Brian')", "expected": "1"},
        ],
        "solution": (
            "def NULL_not_found(object):\n"
            "    if object is None:\n"
            '        print(f"Nothing: {object} {type(object)}")\n'
            "    elif type(object) is float and object != object:\n"
            '        print(f"Cheese: {object} {type(object)}")\n'
            "    elif object is False:\n"
            '        print(f"Fake: {object} {type(object)}")\n'
            "    elif type(object) is int and object == 0:\n"
            '        print(f"Zero: {object} {type(object)}")\n'
            "    elif type(object) is str and object == '':\n"
            '        print(f"Empty: {type(object)}")\n'
            "    else:\n"
            '        print("Type not Found")\n'
            "        return 1\n"
            "    return 0\n"
        ),
        "explanation": (
            "Each 'null-like' value needs its own check because they're "
            "different types with different equality quirks - especially "
            "NaN, whose defining property is that it never equals itself."
        ),
        "concepts": ["None", "NaN", "type", "if/elif", "functions"],
        "skills": ["type_introspection", "edge_case_handling"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-00-whatis",
        "module": "piscine_00_starting",
        "difficulty": 2,
        "title": "The Even and the Odd",
        "description": (
            "Write a script that takes one integer argument on the "
            "command line, and prints \"I'm Even.\" or \"I'm Odd.\" "
            "accordingly.\n\n"
            "If more than one argument is given, or the argument isn't "
            "an integer, print an AssertionError with a clear message "
            "instead of crashing with a raw traceback.\n\n"
            "Allowed: sys, or any other library that gives you the "
            "command-line arguments."
        ),
        "examples": (
            "$> python whatis.py 14\n"
            "I'm Even.\n"
            "$> python whatis.py -5\n"
            "I'm Odd.\n"
            "$> python whatis.py Hi!\n"
            "AssertionError: argument is not an integer\n"
            "$> python whatis.py 13 5\n"
            "AssertionError: more than one argument is provided"
        ),
        "starter_code": "import sys\n\n\ndef main():\n    pass\n\n\nif __name__ == \"__main__\":\n    main()\n",
        "hints": [
            "sys.argv[0] is the script name - the actual arguments start "
            "at sys.argv[1].",
            "Wrap the argument-count and int-parsing checks in try/assert, "
            "and catch AssertionError around your own asserts so you can "
            "print a clean message instead of a traceback.",
            "assert len(sys.argv) == 2, 'more than one argument is "
            "provided'\ntry:\n    n = int(sys.argv[1])\nexcept ValueError:"
            "\n    raise AssertionError('argument is not an integer')",
        ],
        "expected_behavior": (
            "Prints \"I'm Even.\" or \"I'm Odd.\" for a valid single "
            "integer argument."
        ),
        "hidden_tests": [
            {"args": ["14"], "expected_stdout": "I'm Even.", "label": "14 is even"},
            {"args": ["-5"], "expected_stdout": "I'm Odd.", "label": "-5 is odd"},
            {"args": ["0"], "expected_stdout": "I'm Even.", "label": "0 is even"},
        ],
        "solution": (
            "import sys\n\n\n"
            "def main():\n"
            "    try:\n"
            "        assert len(sys.argv) == 2, (\n"
            "            \"AssertionError: more than one argument is provided\"\n"
            "        )\n"
            "        try:\n"
            "            number = int(sys.argv[1])\n"
            "        except ValueError as exc:\n"
            "            raise AssertionError(\n"
            "                \"AssertionError: argument is not an integer\"\n"
            "            ) from exc\n"
            "    except AssertionError as exc:\n"
            "        print(exc)\n"
            "        return\n"
            "    print(\"I'm Even.\" if number % 2 == 0 else \"I'm Odd.\")\n\n\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
        ),
        "explanation": (
            "The argument count is validated before trying to parse it as "
            "an int, and both failure paths are funnelled through a single "
            "assert/except so the script never crashes with a raw "
            "traceback."
        ),
        "concepts": ["sys.argv", "assert", "exceptions", "modulo"],
        "skills": ["cli_argument_handling", "error_handling"],
        "exercise_type": "script",
        **COMMON,
    },
    {
        "id": "piscine-00-building",
        "module": "piscine_00_starting",
        "difficulty": 2,
        "title": "First standalone program (character counts)",
        "description": (
            "Write an autonomous program (with a main) that takes a "
            "single string argument and prints how many characters it "
            "contains in total, then how many are upper-case letters, "
            "lower-case letters, punctuation marks, spaces, and digits.\n\n"
            "If no argument is given, prompt the user for a string "
            "instead. If more than one argument is given, print an "
            "AssertionError."
        ),
        "examples": (
            "$> python building.py \"Ab3! z\"\n"
            "The text contains 6 characters:\n"
            "1 upper letters\n"
            "2 lower letters\n"
            "1 punctuation marks\n"
            "1 spaces\n"
            "1 digits"
        ),
        "starter_code": (
            "import sys\nimport string\n\n\n"
            "def main():\n    pass\n\n\n"
            'if __name__ == "__main__":\n    main()\n'
        ),
        "hints": [
            "The `string` module has ready-made character sets: "
            "string.ascii_uppercase, string.ascii_lowercase, "
            "string.punctuation, string.digits.",
            "Count with a loop and five counters, or with "
            "sum(1 for c in text if c in string.ascii_uppercase) for each "
            "category.",
            "upper = sum(1 for c in text if c.isupper())\nlower = "
            "sum(1 for c in text if c.islower())\npunctuation = sum(1 for "
            "c in text if c in string.punctuation)\nspaces = sum(1 for c "
            "in text if c == ' ')\ndigits = sum(1 for c in text if "
            "c.isdigit())",
        ],
        "expected_behavior": (
            "Prints the total character count, then one line per "
            "category, in the order: upper, lower, punctuation, spaces, "
            "digits."
        ),
        "hidden_tests": [
            {
                "args": ["Ab3! z"],
                "expected_stdout": (
                    "The text contains 6 characters:\n"
                    "1 upper letters\n"
                    "2 lower letters\n"
                    "1 punctuation marks\n"
                    "1 spaces\n"
                    "1 digits"
                ),
                "label": "Test 1",
            }
        ],
        "solution": (
            "import sys\nimport string\n\n\n"
            "def main():\n"
            '    assert len(sys.argv) <= 2, "AssertionError: too many arguments"\n'
            "    text = sys.argv[1] if len(sys.argv) == 2 else input(\n"
            '        "What is the text to count?\\n"\n'
            "    )\n"
            "    upper = sum(1 for c in text if c.isupper())\n"
            "    lower = sum(1 for c in text if c.islower())\n"
            "    punctuation = sum(1 for c in text if c in string.punctuation)\n"
            "    spaces = sum(1 for c in text if c == ' ')\n"
            "    digits = sum(1 for c in text if c.isdigit())\n"
            '    print(f"The text contains {len(text)} characters:")\n'
            '    print(f"{upper} upper letters")\n'
            '    print(f"{lower} lower letters")\n'
            '    print(f"{punctuation} punctuation marks")\n'
            '    print(f"{spaces} spaces")\n'
            '    print(f"{digits} digits")\n\n\n'
            'if __name__ == "__main__":\n'
            "    main()\n"
        ),
        "explanation": (
            "str.isupper()/islower()/isdigit() and membership in "
            "string.punctuation classify each character; summing a "
            "generator expression counts matches without a manual loop "
            "and counter variable."
        ),
        "concepts": ["string module", "sys.argv", "input", "generator expressions"],
        "skills": ["text_processing", "cli_argument_handling"],
        "exercise_type": "script",
        **COMMON,
    },
    {
        "id": "piscine-00-filterstring",
        "module": "piscine_00_starting",
        "difficulty": 2,
        "title": "Dictionaries SoS prep - filter my words",
        "description": (
            "Part 2 of the ft_filter exercise: write a program that "
            "accepts two arguments, a string S and an integer N, and "
            "prints the list of words from S that are longer than N "
            "characters. Words are separated by spaces, and the string "
            "has no punctuation.\n\n"
            "The program must contain at least one list comprehension "
            "and one lambda. If the argument count or types are wrong, "
            "print an AssertionError."
        ),
        "examples": (
            "$> python filterstring.py 'Hello the World' 4\n"
            "['Hello', 'World']\n\n"
            "$> python filterstring.py 'Hello the World' 99\n"
            "[]\n\n"
            "$> python filterstring.py 3 'Hello the World'\n"
            "AssertionError: the arguments are bad"
        ),
        "starter_code": (
            "import sys\n\n\n"
            "def main():\n    pass\n\n\n"
            'if __name__ == "__main__":\n    main()\n'
        ),
        "hints": [
            "Validate argument count first, then try converting the "
            "second argument to int - both failures should raise the "
            "same AssertionError message.",
            "A lambda works well as the filter predicate: "
            "is_long = lambda word: len(word) > n.",
            "words = text.split(' ')\nis_long = lambda w: len(w) > n\nresult "
            "= [w for w in words if is_long(w)]\nprint(result)",
        ],
        "expected_behavior": "Prints a Python list of the matching words.",
        "hidden_tests": [
            {
                "args": ["Hello the World", "4"],
                "expected_stdout": "['Hello', 'World']",
                "label": "Test 1",
            },
            {
                "args": ["Hello the World", "99"],
                "expected_stdout": "[]",
                "label": "Test 2",
            },
        ],
        "solution": (
            "import sys\n\n\n"
            "def main():\n"
            "    try:\n"
            "        assert len(sys.argv) == 3\n"
            "        text = sys.argv[1]\n"
            "        n = int(sys.argv[2])\n"
            "    except (AssertionError, ValueError):\n"
            '        print("AssertionError: the arguments are bad")\n'
            "        return\n"
            "    is_long = lambda word: len(word) > n\n"
            "    words = text.split(' ')\n"
            "    print([word for word in words if is_long(word)])\n\n\n"
            'if __name__ == "__main__":\n'
            "    main()\n"
        ),
        "explanation": (
            "The lambda expresses the 'longer than N' predicate; the "
            "list comprehension applies it to every word in one line, "
            "which is the ft_filter pattern the subject is building "
            "toward."
        ),
        "concepts": ["list comprehension", "lambda", "sys.argv"],
        "skills": ["functional_python", "cli_argument_handling"],
        "exercise_type": "script",
        **COMMON,
    },
    {
        "id": "piscine-00-sos",
        "module": "piscine_00_starting",
        "difficulty": 2,
        "title": "Dictionaries SoS",
        "description": (
            "Write a program that takes a string argument and encodes it "
            "into Morse code, using a dictionary to store the code table. "
            "Complete Morse characters are separated by a single space; "
            "a literal space character becomes a slash (/).\n\n"
            "If the argument count is wrong, or the argument contains "
            "characters your table doesn't cover, print an "
            "AssertionError."
        ),
        "examples": (
            '$> python sos.py "sos" | cat -e\n'
            "... --- ...$\n"
            "$> python sos.py 'h$llo'\n"
            "AssertionError: the arguments are bad"
        ),
        "starter_code": "import sys\n\n\ndef main():\n    pass\n\n\nif __name__ == \"__main__\":\n    main()\n",
        "hints": [
            "You'll need a dictionary mapping every letter/digit (and "
            "space) to its Morse code.",
            "Build the output by looking up each character of the input "
            "in your dictionary and joining the results with a space.",
            "MORSE = {'s': '...', 'o': '---', ' ': '/'}\nprint(' '.join("
            "MORSE[c] for c in text.lower()))",
        ],
        "expected_behavior": "Prints the Morse-encoded string.",
        "hidden_tests": [
            {"args": ["sos"], "expected_stdout": "... --- ...", "label": "sos"},
        ],
        "solution": (
            "import sys\n\n\n"
            "MORSE = {\n"
            "    'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.',\n"
            "    'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---',\n"
            "    'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---',\n"
            "    'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-',\n"
            "    'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--',\n"
            "    'z': '--..', '0': '-----', '1': '.----', '2': '..---',\n"
            "    '3': '...--', '4': '....-', '5': '.....', '6': '-....',\n"
            "    '7': '--...', '8': '---..', '9': '----.', ' ': '/',\n"
            "}\n\n\n"
            "def main():\n"
            "    try:\n"
            "        assert len(sys.argv) == 2\n"
            "        text = sys.argv[1].lower()\n"
            "        code = [MORSE[c] for c in text]\n"
            "    except (AssertionError, KeyError):\n"
            '        print("AssertionError: the arguments are bad")\n'
            "        return\n"
            "    print(' '.join(code))\n\n\n"
            'if __name__ == "__main__":\n'
            "    main()\n"
        ),
        "explanation": (
            "A dictionary maps each character to its Morse code once; "
            "a list comprehension looks each character up, and ' '.join "
            "puts single spaces between the resulting codes."
        ),
        "concepts": ["dict", "sys.argv", "list comprehension", "join"],
        "skills": ["lookup_tables", "cli_argument_handling"],
        "exercise_type": "script",
        **COMMON,
    },
    {
        "id": "piscine-00-loading",
        "module": "piscine_00_starting",
        "difficulty": 3,
        "title": "Loading ... (ft_tqdm)",
        "description": (
            "Write a generator function `ft_tqdm(lst)` that copies the "
            "behaviour of the `tqdm` progress bar package using `yield`, "
            "printing a live percentage/progress bar as the caller "
            "iterates.\n\n"
            "This one is best checked by eye against the real `tqdm` "
            "package side by side (see the subject's tester.py), since "
            "its output updates in place over time rather than producing "
            "a single fixed string - it isn't auto-graded here yet."
        ),
        "examples": (
            "for elem in ft_tqdm(range(333)):\n"
            "    sleep(0.005)\n"
            "-> shows a live progress bar similar to:\n"
            "100%|[===================================>]| 333/333"
        ),
        "starter_code": "def ft_tqdm(lst):\n    # your code here\n    pass\n",
        "hints": [
            "You need to know the total length up front (len(lst)) to "
            "compute a percentage as you go.",
            "os.get_terminal_size() tells you how wide to draw the bar so "
            "it fits the terminal.",
            "for i, item in enumerate(lst):\n    yield item\n    "
            "percent = (i + 1) / len(lst)\n    "
            "print(f'\\r{percent:.0%}|...', end='')",
        ],
        "expected_behavior": (
            "Behaves like a generator wrapping the given iterable, "
            "printing progress as it's consumed."
        ),
        "hidden_tests": [],
        "solution": (
            "import os\n\n\n"
            "def ft_tqdm(lst):\n"
            '    """Yield from lst while printing a tqdm-style progress bar."""\n'
            "    total = len(lst)\n"
            "    width = max(os.get_terminal_size().columns - 20, 10)\n"
            "    for i, item in enumerate(lst):\n"
            "        yield item\n"
            "        done = (i + 1) / total\n"
            "        filled = int(width * done)\n"
            "        bar = ('=' * filled + '>')[:width].ljust(width)\n"
            "        percent = int(done * 100)\n"
            "        print(\n"
            "            f'\\r{percent}%|[{bar}]| {i + 1}/{total}',\n"
            "            end='',\n"
            "        )\n"
            "    print()\n"
        ),
        "explanation": (
            "A generator can run code both before and after each `yield` "
            "- the loop body around the yield is exactly where the "
            "progress percentage gets recomputed and reprinted."
        ),
        "concepts": ["generators", "yield", "os.get_terminal_size"],
        "skills": ["iterators_and_generators"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-00-package",
        "module": "piscine_00_starting",
        "difficulty": 3,
        "title": "My first package creation",
        "description": (
            "Package your own code as an installable Python package (any "
            "way you like) so that:\n"
            "- it appears in `pip list`;\n"
            "- `pip show -v ft_package` prints its metadata;\n"
            "- it installs via either the built sdist (.tar.gz) or wheel "
            "(.whl);\n"
            "- `from ft_package import count_in_list` works, where "
            "`count_in_list(a_list, value)` returns how many times "
            "`value` appears in `a_list`.\n\n"
            "This is a packaging/tooling exercise (pyproject.toml, "
            "build backend, etc.) rather than a single function to grade "
            "automatically - it's included here for completeness of the "
            "learning path, verified manually."
        ),
        "examples": (
            "from ft_package import count_in_list\n"
            'print(count_in_list(["toto", "tata", "toto"], "toto"))  # 2\n'
            'print(count_in_list(["toto", "tata", "toto"], "tutu"))  # 0'
        ),
        "starter_code": "# pyproject.toml / package layout - see description\n",
        "hints": [
            "A minimal package needs a pyproject.toml with [project] "
            "metadata and a src/ft_package/__init__.py.",
            "`count_in_list` is just list.count(value) under the hood.",
            "def count_in_list(items, value):\n    return items.count(value)",
        ],
        "expected_behavior": "pip show -v ft_package succeeds and count_in_list works as shown.",
        "hidden_tests": [],
        "solution": (
            "# ft_package/__init__.py\n"
            "def count_in_list(items, value):\n"
            '    """Return how many times value appears in items."""\n'
            "    return items.count(value)\n"
        ),
        "explanation": (
            "The function itself is one line; the exercise is really "
            "about producing a valid, installable package around it."
        ),
        "concepts": ["packaging", "pyproject.toml", "pip"],
        "skills": ["packaging"],
        "exercise_type": "function",
        **COMMON,
    },
]


def main() -> None:
    EXERCISES_DIR.mkdir(parents=True, exist_ok=True)
    for exercise in EXERCISES:
        out_path = EXERCISES_DIR / f"{exercise['id']}.json"
        out_path.write_text(
            json.dumps(exercise, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out_path.relative_to(ROOT)}")
    print(f"\nTotal 42 Piscine exercises: {len(EXERCISES)}")


if __name__ == "__main__":
    main()
