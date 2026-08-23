# Python-Gym — Sprint 3
## Python Learning Expansion + Learning Foundations

### Goal

Expand Python-Gym substantially before adding more tracks. From Sprint 3 onward,
new UI and educational content must support English and French.

### Sprint 2 continuity

Inspect the actual repository first. Verify Sprint 2 status and fix relevant
regressions before adding content. Do not rebuild working functionality.
Do not invent APIs, models, files, or functions.

Known issues to verify:

- unclear expected input/type requirements and exercise feedback;
- hints that reveal too much of the solution;
- repeated reloads and 500 errors for
  `/exercises?source=progressive_python`.

Add regression tests for fixes.

### Python content expansion

Expand:

- Foundations
- Core Python
- Intermediate Python
- Progressive Python
- 30 Days of Python
- 42 Python Piscine

Add Python-Gym exercises where external sources leave pedagogical gaps.
Use `source = python_gym` for those exercises.

Learning flow:

```
Theory → Foundation → Progressive → Harder application → Source exercise
```

### Foundations

Review and expand: variables, types, input/output, conversions, operators,
conditions, boolean logic, strings, lists, tuples, dictionaries, sets, loops,
functions, scope, and exceptions.

### Intermediate Python

Add progressive coverage for: list/dictionary comprehensions, nested
structures, files, modules, exceptions, iterators, generators, and basic
OOP.

Do not make every topic equally advanced.

### Progressive Python

Expand the existing track so it prepares the student for 42 exercises.
Example:

```
loops → accumulator → loop + condition → loop + list → nested loops → 42
```

Do not simply duplicate Piscine exercises.

### 30 Days of Python

Use: https://github.com/asabeneh/30-days-of-python

Expand the current integration substantially. Preserve
`source = 30_days_python`.

Add difficulty, concepts, skills, prerequisites, examples, and resources
when appropriate. Do not assume every exercise in a day has the same
difficulty.

### 42 Python Piscine

The user-provided PDFs are the source of truth for the seed. Do not invent
exercises or silently change requirements, restrictions, examples, or
expected behavior.

The PDFs do not need to be copied into the repository.

#### Excluded exercise

The Piscine 0 compression exercise remains excluded:

- not active;
- not in the learning path;
- not pending;
- not required for completion.

### Resources

Create/use: `resources/`

Support resources such as CSV, JSON, text files, datasets, examples, and
reference material. Exercises must be able to declare their resources.
Avoid unnecessary duplication.

### Learning Notes

Create educational notes, starting with:

- Lists
- Dictionaries

Then add notes where justified: Strings, Loops, Functions, Tuples, Sets,
Exceptions, Comprehensions, Files, Modules, OOP.

Each note should contain: explanation, basic syntax, examples, practical
examples, common mistakes, mini exercises, related practice.

Avoid giant walls of documentation.

#### Lists note

Cover, as appropriate: creating lists, indexing, negative indexing,
slicing, modification, append, extend, insert, remove, pop, clear, sort,
reverse, len, iteration, membership, nested lists, and list comprehensions.

#### Dictionaries note

Cover, as appropriate: creation, keys/values, access, add/modify/delete,
keys(), values(), items(), iteration, membership, nested dictionaries, and
comprehensions.

### Skills, concepts, prerequisites

Reuse the existing metadata architecture. Avoid duplicate concept names.

Prerequisites should represent learning order, for example:
`nested_loops` requires `loops` and `conditions`.

Do not implement a complex prerequisite algorithm yet.

### Learning Path

Create a basic path using: difficulty, concepts, skills, prerequisites,
source, solved status, repeat status, mastery.

Do not equate passing tests with mastery. Preserve Repeat as distinct from
mastery. Do not implement advanced spaced repetition yet.

### Adaptive difficulty preparation

Do not build a complex adaptive engine yet. Ensure data can later detect
repeated successful completion, no hints, no solution reveal, low error
rate, and reliable completion.

The future system should stop repeating exercises the student clearly
masters and move toward harder variants. This is especially important for
future Exam Mode.

### Repeat

Preserve Sprint 2 behavior. `SOLVED_TO_REPEAT` must not become `MASTERED`.
Do not implement full spaced repetition in Sprint 3.

### English + French

From Sprint 3 onward, new UI and educational content must support English
and French. Use the existing localization approach if one exists. Do not
invent a localization framework unnecessarily. Provide a clear fallback for
content not yet translated.

### Sidebar

Expose:

```
Python
  - Foundations
  - Progressive Python
  - 30 Days of Python
  - 42 Python Piscine
```

Learning Notes may be accessible from the Python area. Do not activate
future tracks prematurely.

### Sprint 4 preparation

Sprint 4 will focus on:

**SQL**: SQL Foundations, Progressive SQL, SQL Challenges

**Interviews**: Interview Foundations, Python Interview Practice,
preparation for LeetCode Top Interview 150

Reuse: track, source, concepts, skills, prerequisites, difficulty,
attempts, and progress.

Sprint 3 must NOT implement complete SQL or Interview tracks. Sprint 4 must
not yet implement full Exam Mode, ML, or ML Piscine.

### Code quality rules

- ONLY use uv; NEVER use pip.
- Type hints required.
- Public APIs require docstrings.
- Functions must be small and focused.
- Maximum line length: 88 characters.
- PEP 8.
- Use f-strings.
- New functionality requires tests.
- Bug fixes require regression tests.
- Prefer simple code over clever code.
- Follow existing architecture.

#### Comments

No comments longer than 50 lines. Comments should explain non-obvious
decisions, not narrate obvious code. Prefer readable code and focused
docstrings.

#### No phantom functions

Never call, document, or reference functions that do not exist. Inspect
actual implementations and follow existing names. Add functions only for
real requirements; do not create speculative APIs.

### Tests

Test at minimum: Python retrieval, seed loading, source filtering,
difficulty, skills, concepts, prerequisites, learning notes, resources,
learning path, repeat + progress, mastery + repeat, English localization,
French localization, 30 Days content, 42 content, excluded compression
exercise, Sprint 2 regressions.

Run: `uv run pytest`. All tests must pass.

### Mandatory Sprint Review

Do NOT start Sprint 4 automatically.

At the end of Sprint 3 report:

**Changes**: what changed and why; files added and modified;
model/API/frontend changes.

**Content**: Python-Gym exercises added; Progressive exercises added;
30 Days exercises added; 42 exercises added; excluded exercises; learning
notes; resources.

**Tests**: tests added; regression tests; important scenarios; final
`uv run pytest` result.

**Regression check**: for important changes, document Before / After / Why
/ Risk. Explicitly verify Sprint 1 and Sprint 2 functionality still works.

**Problems**: report remaining bugs, technical debt, incomplete
translations, content gaps, and architectural concerns.

**Next sprint**: propose Sprint 4 scope. Do not implement Sprint 4 during
the review.

### Definition of Done

- [ ] Python catalog substantially expanded
- [ ] Progressive Python expanded
- [ ] 30 Days substantially expanded
- [ ] 42 content correctly seeded
- [ ] compression remains excluded
- [ ] Python-Gym exercises fill important gaps
- [ ] resources are usable
- [ ] Lists note exists
- [ ] Dictionaries note exists
- [ ] additional notes added where justified
- [ ] skills/concepts consistent
- [ ] prerequisites represented
- [ ] basic learning path works
- [ ] Repeat and mastery preserved
- [ ] English support exists
- [ ] French support exists
- [ ] Sprint 2 regressions fixed/tested
- [ ] tests pass
- [ ] no phantom functions
- [ ] no comments over 50 lines
- [ ] no unnecessary refactors
- [ ] Sprint Review completed
- [ ] Sprint 4 not started automatically
