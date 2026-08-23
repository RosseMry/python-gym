"""Generates exercise JSON files for 42 Piscine Modules 3 and 4.

Module 3 - "Oriented Object Programming" (en_subject_4.pdf)
Module 4 - "Data Oriented Design" (en_subject_5.pdf)

Both are pure Python (no numpy/pandas), unlike Modules 1-2 of the same
series, so they fit inside Sprint 2's scope. As with module 0, not
every exercise here maps cleanly onto the current call/script hidden
test model (dunder methods with side-effect prints, decorators with
persistent internal state across many calls, an abstract base class
that's supposed to raise on direct instantiation). Those are included
with full metadata and no hidden tests rather than forced into a
grading shape that doesn't match what the subject actually asks for -
see Sprint 2 spec section 40 ("si existe ambigüedad, marcarla... en
lugar de inventar").
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
    # Module 3 - Oriented Object Programming (en_subject_4.pdf)
    # ---------------------------------------------------------------
    {
        "id": "piscine-03-got-s1e9",
        "module": "piscine_03_oop",
        "difficulty": 2,
        "title": "GOT S1E9 (abstract Character class)",
        "description": (
            "Create an abstract class `Character` (using `abc.ABC` and "
            "`@abstractmethod`) that takes `first_name` as its first "
            "parameter and `is_alive` as an optional second parameter "
            "defaulting to True. It must not be possible to instantiate "
            "`Character` directly.\n\n"
            "Create a `Stark` class that inherits from `Character`, with "
            "a `die()` method that sets `is_alive` to False."
        ),
        "examples": (
            "Ned = Stark('Ned')\n"
            "print(Ned.__dict__)   # {'first_name': 'Ned', 'is_alive': True}\n"
            "Ned.die()\n"
            "print(Ned.is_alive)   # False\n\n"
            "Character('hodor')  # TypeError: Can't instantiate abstract "
            "class Character with abstract method ..."
        ),
        "starter_code": (
            "from abc import ABC, abstractmethod\n\n\n"
            "class Character(ABC):\n"
            '    """Your docstring for Class"""\n\n'
            "    @abstractmethod\n"
            "    def __init__(self, first_name, is_alive=True):\n"
            "        pass\n\n\n"
            "class Stark(Character):\n"
            '    """Your docstring for Class"""\n'
            "    # your code here\n"
        ),
        "hints": [
            "Marking __init__ itself as @abstractmethod is enough to "
            "block direct instantiation of Character, as long as Stark "
            "provides its own concrete __init__.",
            "Stark's __init__ needs to actually set self.first_name and "
            "self.is_alive - inheriting from an abstract class doesn't "
            "give you that for free.",
            "class Stark(Character):\n    def __init__(self, first_name, "
            "is_alive=True):\n        self.first_name = first_name\n"
            "        self.is_alive = is_alive\n\n    def die(self):\n"
            "        self.is_alive = False",
        ],
        "expected_behavior": (
            "Stark('Ned').__dict__ == {'first_name': 'Ned', 'is_alive': "
            "True}; calling die() flips is_alive to False; Character(...) "
            "cannot be instantiated directly."
        ),
        "hidden_tests": [
            {
                "call": "Stark('Ned').__dict__",
                "expected": "{'first_name': 'Ned', 'is_alive': True}",
                "label": "Stark defaults",
            },
            {
                "call": "Stark('Lyanna', False).__dict__",
                "expected": "{'first_name': 'Lyanna', 'is_alive': False}",
                "label": "Stark explicit is_alive",
            },
            {
                "call": "(lambda c: (c.die(), c.is_alive)[1])(Stark('Ned'))",
                "expected": "False",
                "label": "die() flips is_alive",
            },
        ],
        "solution": (
            "from abc import ABC, abstractmethod\n\n\n"
            "class Character(ABC):\n"
            '    """A character that may or may not still be alive."""\n\n'
            "    @abstractmethod\n"
            "    def __init__(self, first_name, is_alive=True):\n"
            '        """Store the first name and life status."""\n'
            "        self.first_name = first_name\n"
            "        self.is_alive = is_alive\n\n"
            "    def die(self):\n"
            '        """Mark this character as no longer alive."""\n'
            "        self.is_alive = False\n\n\n"
            "class Stark(Character):\n"
            '    """A member of House Stark."""\n\n'
            "    def __init__(self, first_name, is_alive=True):\n"
            '        """Build a Stark with a name and life status."""\n'
            "        super().__init__(first_name, is_alive)\n"
        ),
        "explanation": (
            "@abstractmethod on __init__ prevents Character() itself "
            "from being built, but any concrete subclass that defines its "
            "own __init__ (even one that just calls super().__init__()) "
            "satisfies the ABC and can be instantiated normally."
        ),
        "concepts": ["abc", "abstractmethod", "inheritance", "__dict__"],
        "skills": ["object_oriented_design"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-03-got-s1e7",
        "module": "piscine_03_oop",
        "difficulty": 3,
        "title": "GOT S1E7 (two families + a class method)",
        "description": (
            "Create `Baratheon` and `Lannister` classes that inherit from "
            "`Character` and can be instantiated directly (without going "
            "through `Character`), each with its own `family_name`, "
            "`eyes` and `hairs`. Make `__str__`/`__repr__` return strings "
            "(not the objects they wrap). Add a class method on "
            "`Lannister` to create Lannister characters in a chain.\n\n"
            "This is not auto-graded here: __str__/__repr__ returning "
            "strings that read like 'Representing the Baratheon family.' "
            "involves the exact wording being up to the student, so hidden "
            "tests would just be checking against fabricated wording, not "
            "the actual requirement. Verify against the subject's own "
            "tester.py."
        ),
        "examples": (
            "Robert = Baratheon('Robert')\n"
            "print(Robert.__dict__)\n"
            "# {'first_name': 'Robert', 'is_alive': True, "
            "'family_name': 'Baratheon', 'eyes': 'brown', 'hairs': 'dark'}\n\n"
            "Jaine = Lannister.create_lannister('Jaine', True)\n"
            "print(Jaine.first_name, Jaine.is_alive)  # Jaine True"
        ),
        "starter_code": (
            "from S1E9 import Character\n\n\n"
            "class Baratheon(Character):\n"
            "    # your code here\n"
            "    pass\n\n\n"
            "class Lannister(Character):\n"
            "    # your code here\n"
            "    pass\n"
        ),
        "hints": [
            "Each family subclass needs its own __init__ that calls "
            "Character.__init__ (via super()) and then sets its own "
            "extra attributes (family_name, eyes, hairs).",
            "__str__ and __repr__ are just methods - define them to "
            "return an f-string instead of the default object repr.",
            "A @classmethod receives the class itself as its first "
            "argument (conventionally `cls`), so it can call `cls(...)` "
            "to build and return a new instance.",
        ],
        "expected_behavior": (
            "Baratheon/Lannister instantiate without going through "
            "Character; __str__/__repr__ return strings; "
            "Lannister.create_lannister(name, alive) returns a new "
            "Lannister."
        ),
        "hidden_tests": [],
        "solution": (
            "from S1E9 import Character\n\n\n"
            "class Baratheon(Character):\n"
            '    """A member of House Baratheon."""\n\n'
            "    def __init__(self, first_name, is_alive=True):\n"
            "        super().__init__(first_name, is_alive)\n"
            "        self.family_name = 'Baratheon'\n"
            "        self.eyes = 'brown'\n"
            "        self.hairs = 'dark'\n\n"
            "    def __str__(self):\n"
            "        return 'Representing the Baratheon family.'\n\n"
            "    def __repr__(self):\n"
            "        return 'Representing the Baratheon family.'\n\n\n"
            "class Lannister(Character):\n"
            '    """A member of House Lannister."""\n\n'
            "    def __init__(self, first_name, is_alive=True):\n"
            "        super().__init__(first_name, is_alive)\n"
            "        self.family_name = 'Lannister'\n"
            "        self.eyes = 'blue'\n"
            "        self.hairs = 'light'\n\n"
            "    def __str__(self):\n"
            "        return 'Representing the Lannister family.'\n\n"
            "    @classmethod\n"
            "    def create_lannister(cls, first_name, is_alive=True):\n"
            '        """Build a new Lannister - a chainable factory."""\n'
            "        return cls(first_name, is_alive)\n"
        ),
        "explanation": (
            "super().__init__(...) reuses Character's constructor logic "
            "instead of repeating it; a classmethod factory is just a "
            "regular method decorated with @classmethod that returns "
            "cls(...) - it's the idiomatic way to offer an alternative "
            "constructor."
        ),
        "concepts": ["inheritance", "super", "__str__", "__repr__", "classmethod"],
        "skills": ["object_oriented_design"],
        "exercise_type": "function",
        "prerequisites": ["piscine-03-got-s1e9"],
        **COMMON,
    },
    {
        "id": "piscine-03-diamond-trap",
        "module": "piscine_03_oop",
        "difficulty": 4,
        "title": "Now it's weird! (diamond inheritance + properties)",
        "description": (
            "Create a `King` class that inherits from both `Baratheon` "
            "and `Lannister` (multiple inheritance - a 'diamond' since "
            "both ultimately inherit from `Character`). Use properties "
            "so that `eyes`/`hairs` are read through `get_eyes()`/"
            "`get_hairs()` and written through `set_eyes()`/"
            "`set_hairs()`.\n\n"
            "Python resolves the diamond via C3 linearization (MRO) "
            "since Python 2.3, so King(Baratheon, Lannister) is well "
            "defined - worth reading up on `ClassName.__mro__`."
        ),
        "examples": (
            "Joffrey = King('Joffrey')\n"
            "Joffrey.set_eyes('blue')\n"
            "print(Joffrey.get_eyes())  # blue"
        ),
        "starter_code": (
            "from S1E7 import Baratheon, Lannister\n\n\n"
            "class King(Baratheon, Lannister):\n"
            "    # your code here\n"
            "    pass\n"
        ),
        "hints": [
            "King doesn't need its own __init__ if Baratheon's is "
            "suitable - multiple inheritance still follows the MRO for "
            "attribute/method lookup.",
            "A property pair looks like: a plain attribute (e.g. "
            "self._eyes) plus get_eyes()/set_eyes() methods that read and "
            "write it.",
            "def get_eyes(self):\n    return self.eyes\n\ndef set_eyes"
            "(self, value):\n    self.eyes = value",
        ],
        "expected_behavior": (
            "King inherits Baratheon's attributes by default (via MRO), "
            "and get/set methods let you change eyes/hairs afterward."
        ),
        "hidden_tests": [],
        "solution": (
            "from S1E7 import Baratheon, Lannister\n\n\n"
            "class King(Baratheon, Lannister):\n"
            '    """The one true king - or so he thinks."""\n\n'
            "    def get_eyes(self):\n"
            '        """Return the current eye colour."""\n'
            "        return self.eyes\n\n"
            "    def set_eyes(self, value):\n"
            '        """Update the eye colour."""\n'
            "        self.eyes = value\n\n"
            "    def get_hairs(self):\n"
            '        """Return the current hair colour."""\n'
            "        return self.hairs\n\n"
            "    def set_hairs(self, value):\n"
            '        """Update the hair colour."""\n'
            "        self.hairs = value\n"
        ),
        "explanation": (
            "Python's C3 linearization gives King a single, consistent "
            "MRO even though Baratheon and Lannister both descend from "
            "Character, so `King(Baratheon, Lannister)` is unambiguous "
            "about which __init__ runs first (Baratheon's)."
        ),
        "concepts": ["multiple inheritance", "MRO", "properties"],
        "skills": ["object_oriented_design"],
        "exercise_type": "function",
        "prerequisites": ["piscine-03-got-s1e7"],
        **COMMON,
    },
    {
        "id": "piscine-03-calculator-vector",
        "module": "piscine_03_oop",
        "difficulty": 3,
        "title": "Calculate my vector",
        "description": (
            "Write a `calculator` class whose `__add__`, `__mul__`, "
            "`__sub__` and `__truediv__` methods each take a vector "
            "(a list of floats) and a scalar, print the elementwise "
            "result, and return None. Division by zero should be "
            "handled explicitly (this is the one error case the subject "
            "asks you to handle)."
        ),
        "examples": (
            "v1 = calculator([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])\n"
            "v1 + 5\n"
            "# prints [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]"
        ),
        "starter_code": (
            "class calculator:\n"
            "    # your code here\n\n"
            "    def __add__(self, other):\n"
            "        pass\n\n"
            "    def __mul__(self, other):\n"
            "        pass\n\n"
            "    def __sub__(self, other):\n"
            "        pass\n\n"
            "    def __truediv__(self, other):\n"
            "        pass\n"
        ),
        "hints": [
            "__add__(self, other) is called automatically for `instance "
            "+ other` - `other` here is the scalar on the right-hand "
            "side.",
            "Each dunder method should build a new list applying the "
            "operation to every element of self's stored vector, then "
            "print it (the prototype return type is None, not the new "
            "vector).",
            "def __add__(self, other):\n    print([x + other for x in "
            "self.values])",
        ],
        "expected_behavior": (
            "Each operator prints the elementwise result list; dividing "
            "by 0 is handled without crashing."
        ),
        "hidden_tests": [],
        "solution": (
            "class calculator:\n"
            '    """Elementwise vector/scalar arithmetic, printed in place."""\n\n'
            "    def __init__(self, values):\n"
            '        """Store the vector this calculator wraps."""\n'
            "        self.values = values\n\n"
            "    def __add__(self, other):\n"
            '        """Print self + other, elementwise."""\n'
            "        print([x + other for x in self.values])\n\n"
            "    def __mul__(self, other):\n"
            '        """Print self * other, elementwise."""\n'
            "        print([x * other for x in self.values])\n\n"
            "    def __sub__(self, other):\n"
            '        """Print self - other, elementwise."""\n'
            "        print([x - other for x in self.values])\n\n"
            "    def __truediv__(self, other):\n"
            '        """Print self / other, elementwise (guards against 0)."""\n'
            "        if other == 0:\n"
            '            print("Error: division by zero")\n'
            "            return\n"
            "        print([x / other for x in self.values])\n"
        ),
        "explanation": (
            "Operator overloading via dunder methods lets `v1 + 5` call "
            "v1.__add__(5) automatically; the subject asks for the side "
            "effect (printing) rather than a returned value, which is "
            "why every method ends in print(...) instead of return."
        ),
        "concepts": ["dunder methods", "operator overloading"],
        "skills": ["object_oriented_design"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-03-calculator-dotproduct",
        "module": "piscine_03_oop",
        "difficulty": 3,
        "title": "Calculate my dot product",
        "description": (
            "Extend the calculator with `dotproduct`, `add_vec` and "
            "`sous_vec` methods that work on two same-length vectors "
            "(dot product, elementwise addition, elementwise "
            "subtraction). These should be usable without instantiating "
            "the class at all - `calculator.dotproduct(a, b)` should "
            "work directly, which calls for a decorator."
        ),
        "examples": (
            "a = [5, 10, 2]\n"
            "b = [2, 4, 3]\n"
            "calculator.dotproduct(a, b)  # Dot product is: 56\n"
            "calculator.add_vec(a, b)     # Add Vector is : [7.0, 14.0, 5.0]\n"
            "calculator.sous_vec(a, b)    # Sous Vector is: [3.0, 6.0, -1.0]"
        ),
        "starter_code": (
            "class calculator:\n"
            "    # your code here\n\n"
            "    # decorator\n"
            "    def dotproduct(V1, V2):\n"
            "        pass\n\n"
            "    # decorator\n"
            "    def add_vec(V1, V2):\n"
            "        pass\n\n"
            "    # decorator\n"
            "    def sous_vec(V1, V2):\n"
            "        pass\n"
        ),
        "hints": [
            "Calling a method on the class itself, not an instance "
            "(calculator.dotproduct(...) rather than "
            "calculator().dotproduct(...)), is exactly what "
            "@staticmethod is for.",
            "No error handling is required here - vectors are guaranteed "
            "to be the same length.",
            "@staticmethod\ndef dotproduct(V1, V2):\n    print('Dot "
            "product is:', sum(x * y for x, y in zip(V1, V2)))",
        ],
        "expected_behavior": "Each method can be called directly on the class, and prints its result.",
        "hidden_tests": [],
        "solution": (
            "class calculator:\n"
            '    """Vector-to-vector operations usable without an instance."""\n\n'
            "    @staticmethod\n"
            "    def dotproduct(V1, V2):\n"
            '        """Print the dot product of V1 and V2."""\n'
            "        result = sum(x * y for x, y in zip(V1, V2))\n"
            "        print(f'Dot product is: {result}')\n\n"
            "    @staticmethod\n"
            "    def add_vec(V1, V2):\n"
            '        """Print the elementwise sum of V1 and V2."""\n'
            "        result = [float(x + y) for x, y in zip(V1, V2)]\n"
            "        print(f'Add Vector is : {result}')\n\n"
            "    @staticmethod\n"
            "    def sous_vec(V1, V2):\n"
            '        """Print the elementwise difference of V1 and V2."""\n'
            "        result = [float(x - y) for x, y in zip(V1, V2)]\n"
            "        print(f'Sous Vector is: {result}')\n"
        ),
        "explanation": (
            "@staticmethod removes the implicit `self`/`cls` first "
            "argument, so the method behaves like a plain function "
            "namespaced under the class - exactly what's needed to call "
            "it as `calculator.dotproduct(a, b)` with no instance."
        ),
        "concepts": ["staticmethod", "decorators", "zip", "dot product"],
        "skills": ["object_oriented_design"],
        "exercise_type": "function",
        "prerequisites": ["piscine-03-calculator-vector"],
        **COMMON,
    },
    # ---------------------------------------------------------------
    # Module 4 - Data Oriented Design (en_subject_5.pdf)
    # ---------------------------------------------------------------
    {
        "id": "piscine-04-outer-inner",
        "module": "piscine_04_data_oriented_design",
        "difficulty": 3,
        "title": "Outer_inner (closures)",
        "description": (
            "Write `square(x)` (returns x squared), `pow(x)` (returns x "
            "raised to itself), and `outer(x, function)` which returns a "
            "callable `inner()` that, each time it's called, applies "
            "`function` to `x` raised to an internal call-count power "
            "(so repeated calls give repeatedly-exponentiated results) - "
            "without using any global variable."
        ),
        "examples": (
            "my_counter = outer(3, square)\n"
            "print(my_counter())  # 9\n"
            "print(my_counter())  # 81\n"
            "print(my_counter())  # 6561"
        ),
        "starter_code": (
            "def square(x):\n    # your code here\n    pass\n\n\n"
            "def pow(x):\n    # your code here\n    pass\n\n\n"
            "def outer(x, function):\n"
            "    count = 0\n\n"
            "    def inner():\n"
            "        # your code here\n"
            "        pass\n\n"
            "    return inner\n"
        ),
        "hints": [
            "`count` needs to change between calls to `inner()` without "
            "being a global - that's exactly what a closure variable in "
            "the enclosing `outer()` scope is for.",
            "Modifying a variable from an enclosing (not global) scope "
            "inside a nested function requires the `nonlocal` keyword.",
            "def inner():\n    nonlocal count\n    count += 1\n    return "
            "function(x ** count)",
        ],
        "expected_behavior": (
            "Each call to the returned inner() applies function to x "
            "raised to an increasing power, starting from the first call."
        ),
        "hidden_tests": [
            {"call": "outer(3, square)()", "expected": "9", "label": "square, 1st call"},
            {"call": "outer(1.5, pow)()", "expected": "1.8371173070873836", "label": "pow, 1st call"},
        ],
        "solution": (
            "def square(x):\n"
            '    """Return x squared."""\n'
            "    return x ** 2\n\n\n"
            "def pow(x):\n"
            '    """Return x raised to the power of itself."""\n'
            "    return x ** x\n\n\n"
            "def outer(x, function):\n"
            '    """Return a counter closure applying function to x^n."""\n'
            "    count = 0\n\n"
            "    def inner():\n"
            '        """Apply function to x raised to the call count."""\n'
            "        nonlocal count\n"
            "        count += 1\n"
            "        return function(x ** count)\n\n"
            "    return inner\n"
        ),
        "explanation": (
            "`inner()` closes over both `x` and `count` from `outer()`'s "
            "scope. `nonlocal count` is what lets it mutate that "
            "enclosing variable across separate calls, instead of "
            "creating a fresh local each time (which plain assignment "
            "would do)."
        ),
        "concepts": ["closures", "nonlocal", "nested functions"],
        "skills": ["functional_python"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-04-calllimit",
        "module": "piscine_04_data_oriented_design",
        "difficulty": 3,
        "title": "My first decorating (call limit)",
        "description": (
            "Write `callLimit(limit)`, a decorator factory that blocks a "
            "function from running more than `limit` times, printing an "
            "error message (naming the function and its memory address, "
            "in the style of the subject's example) once the limit is "
            "exceeded instead of calling it again.\n\n"
            "Not auto-graded: the expected output embeds the wrapped "
            "function's memory address (`0x7fabdc243ee0`-style), which is "
            "different every run and every machine, so an exact-match "
            "hidden test isn't meaningful here."
        ),
        "examples": (
            "@callLimit(1)\n"
            "def g():\n"
            "    print('g()')\n\n"
            "g()  # g()\n"
            "g()  # Error: <function g at 0x...> call too many times"
        ),
        "starter_code": (
            "def callLimit(limit):\n"
            "    count = 0\n\n"
            "    def callLimiter(function):\n"
            "        def limit_function(*args, **kwds):\n"
            "            # your code here\n"
            "            pass\n"
            "        return limit_function\n\n"
            "    return callLimiter\n"
        ),
        "hints": [
            "Each decorated function needs its own independent call "
            "counter - putting `count = 0` at the `callLimit(limit)` "
            "level (not `limit_function` level) gives every decorated "
            "function its own closure over a fresh `count`.",
            "`nonlocal count` again, same reasoning as the previous "
            "exercise's inner().",
            "def limit_function(*args, **kwds):\n    nonlocal count\n"
            "    if count >= limit:\n        print(f'Error: {function} "
            "call too many times')\n        return\n    count += 1\n"
            "    return function(*args, **kwds)",
        ],
        "expected_behavior": "Calls beyond the limit print an error instead of running the function.",
        "hidden_tests": [],
        "solution": (
            "def callLimit(limit):\n"
            '    """Decorator factory limiting how many times a function runs."""\n'
            "    count = 0\n\n"
            "    def callLimiter(function):\n"
            '        """Wrap function with the call-limit check."""\n'
            "        def limit_function(*args, **kwds):\n"
            "            nonlocal count\n"
            "            if count >= limit:\n"
            "                print(f'Error: {function} call too many times')\n"
            "                return None\n"
            "            count += 1\n"
            "            return function(*args, **kwds)\n"
            "        return limit_function\n\n"
            "    return callLimiter\n"
        ),
        "explanation": (
            "callLimit(limit) is a decorator *factory*: calling it "
            "returns callLimiter, the actual decorator, which closes over "
            "both `limit` and a per-function `count`."
        ),
        "concepts": ["decorators", "closures", "*args", "**kwargs"],
        "skills": ["functional_python"],
        "exercise_type": "function",
        "prerequisites": ["piscine-04-outer-inner"],
        **COMMON,
    },
    {
        "id": "piscine-04-statistics",
        "module": "piscine_04_data_oriented_design",
        "difficulty": 3,
        "title": "Calculate my statistics",
        "description": (
            "Write `ft_statistics(*args, **kwargs)`: `args` are the "
            "numbers to analyse, and `kwargs` picks which statistics to "
            "print - the *value* of each kwarg names the statistic "
            "(mean, median, quartile, std, var), regardless of what the "
            "keyword's own name is. Handle bad input (e.g. no numbers, "
            "or an unrecognised statistic name) by printing 'ERROR' "
            "instead of crashing."
        ),
        "examples": (
            "ft_statistics(1, 42, 360, 11, 64, toto='mean', tutu='median', "
            "tata='quartile')\n"
            "# mean : 95.6\n"
            "# median : 42\n"
            "# quartile : [11.0, 64.0]"
        ),
        "starter_code": (
            "def ft_statistics(*args, **kwargs):\n"
            "    # your code here\n"
            "    pass\n"
        ),
        "hints": [
            "It's the *values* of kwargs that matter ('mean', 'median', "
            "...), not their key names - loop over kwargs.values(), not "
            "kwargs.keys().",
            "Guard the whole per-statistic computation in a try/except so "
            "an unknown statistic name, or an empty args, prints 'ERROR' "
            "for that entry instead of stopping the whole function.",
            "for stat in kwargs.values():\n    try:\n        if stat == "
            "'mean':\n            print('mean :', sum(args) / len(args))\n"
            "        ...\n    except (ZeroDivisionError, ValueError):\n"
            "        print('ERROR')",
        ],
        "expected_behavior": (
            "Prints one line per requested statistic, in the order "
            "given, or 'ERROR' for anything it can't compute."
        ),
        "hidden_tests": [],
        "solution": (
            "def ft_statistics(*args, **kwargs):\n"
            '    """Print the requested statistics for the given numbers."""\n'
            "    for stat in kwargs.values():\n"
            "        try:\n"
            "            if not args:\n"
            "                raise ValueError('no data')\n"
            "            ordered = sorted(args)\n"
            "            n = len(ordered)\n"
            "            if stat == 'mean':\n"
            "                print('mean :', sum(args) / n)\n"
            "            elif stat == 'median':\n"
            "                mid = n // 2\n"
            "                if n % 2 == 0:\n"
            "                    print('median :', (ordered[mid - 1] + ordered[mid]) / 2)\n"
            "                else:\n"
            "                    print('median :', ordered[mid])\n"
            "            elif stat == 'quartile':\n"
            "                q1 = ordered[n // 4]\n"
            "                q3 = ordered[(3 * n) // 4]\n"
            "                print('quartile :', [float(q1), float(q3)])\n"
            "            elif stat == 'std':\n"
            "                mean = sum(args) / n\n"
            "                variance = sum((x - mean) ** 2 for x in args) / n\n"
            "                print('std :', variance ** 0.5)\n"
            "            elif stat == 'var':\n"
            "                mean = sum(args) / n\n"
            "                variance = sum((x - mean) ** 2 for x in args) / n\n"
            "                print('var :', variance)\n"
            "            else:\n"
            "                raise ValueError('unknown statistic')\n"
            "        except (ValueError, ZeroDivisionError):\n"
            "            print('ERROR')\n"
        ),
        "explanation": (
            "**kwargs is a plain dict, so its .values() give the "
            "statistic names the caller asked for regardless of what "
            "they named the keyword itself - that indirection is the "
            "whole point of the exercise."
        ),
        "concepts": ["*args", "**kwargs", "statistics", "error handling"],
        "skills": ["functional_python", "numerical_computation"],
        "exercise_type": "function",
        **COMMON,
    },
    {
        "id": "piscine-04-dataclass-student",
        "module": "piscine_04_data_oriented_design",
        "difficulty": 2,
        "title": "Data class (Student)",
        "description": (
            "Write a `@dataclass` `Student` with `name` and `surname` as "
            "required fields, `active` defaulting to True, a `login` "
            "computed from name/surname (first letter of the name + full "
            "surname, capitalised), and a random 15-character `id` from "
            "`generate_id()`. Neither `login` nor `id` should be "
            "settable via the constructor - passing `id=...` should "
            "raise a TypeError. Do not define `__str__`/`__repr__` "
            "yourself - use the dataclass-generated one."
        ),
        "examples": (
            "student = Student(name='Edward', surname='agle')\n"
            "print(student)\n"
            "# Student(name='Edward', surname='agle', active=True, "
            "login='Eagle', id='trannxhndgtolvh')"
        ),
        "starter_code": (
            "import random\nimport string\n"
            "from dataclasses import dataclass, field\n\n\n"
            "def generate_id():\n"
            '    """Return a random 15-character lowercase id."""\n'
            "    return \"\".join(random.choices(string.ascii_lowercase, k=15))\n\n\n"
            "@dataclass\n"
            "class Student:\n"
            "    # your code here\n"
            "    pass\n"
        ),
        "hints": [
            "`login` and `id` both depend on other fields (or on "
            "randomness), so they can't be plain constructor parameters "
            "- they need `field(init=False, ...)`.",
            "`field(default_factory=generate_id)` computes `id` once per "
            "instance, at construction time, without it being a "
            "settable argument.",
            "A field with no default set directly in __post_init__ (or "
            "computed via default_factory referencing other fields "
            "indirectly) is one way to derive login from name/surname "
            "after the other fields are set.",
        ],
        "expected_behavior": (
            "Student(name=..., surname=...) works; Student(..., id=...) "
            "raises TypeError; the printed repr shows all five fields."
        ),
        "hidden_tests": [],
        "solution": (
            "import random\nimport string\n"
            "from dataclasses import dataclass, field\n\n\n"
            "def generate_id():\n"
            '    """Return a random 15-character lowercase id."""\n'
            "    return \"\".join(random.choices(string.ascii_lowercase, k=15))\n\n\n"
            "@dataclass\n"
            "class Student:\n"
            '    """A student with an auto-generated login and id."""\n\n'
            "    name: str\n"
            "    surname: str\n"
            "    active: bool = True\n"
            "    login: str = field(init=False)\n"
            "    id: str = field(init=False, default_factory=generate_id)\n\n"
            "    def __post_init__(self):\n"
            '        """Derive login from name and surname."""\n'
            "        self.login = self.name[0].upper() + self.surname.lower()\n"
        ),
        "explanation": (
            "`field(init=False)` removes a field from the generated "
            "__init__ signature entirely, so passing it as a keyword "
            "argument raises TypeError. `__post_init__` runs right after "
            "the generated __init__, which is where `login` can be "
            "derived from the already-set `name`/`surname`."
        ),
        "concepts": ["dataclasses", "field", "__post_init__"],
        "skills": ["data_modeling"],
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
    print(f"\nTotal Module 3+4 exercises: {len(EXERCISES)}")


if __name__ == "__main__":
    main()
