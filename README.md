# Python Gym — Sprint 2

A local practice platform to build Python fluency for Machine Learning,
by making you write code from scratch instead of copying it.

Sprint 1 built the core engine (exercises, code editor, sandboxed
execution, hints, progress/mastery). Sprint 2 (this state) improves
execution feedback, adds a repeat queue, expands the exercise model,
and brings in real content from three sources: Progressive Python,
30 Days of Python, and the 42 Python Piscine. See
[`SPRINT_2_REVIEW.md`](./SPRINT_2_REVIEW.md) for the full sprint review.

## Architecture

```
backend/            FastAPI + SQLite, layered:
  app/api/           HTTP routes (thin — parse request, call service, shape response)
  app/domain/         Plain dataclasses: Exercise, HiddenTest, SubmissionResult, ...
  app/services/        Business rules: hints, mastery, repeat, execution, style checks
  app/repositories/     SQLite persistence, no business logic
  app/models/database.py  Schema + connection (auto-migrates old DBs)
  scripts/seed.py       Loads exercises/*.json into SQLite
  tests/               pytest suite (61 tests: unit + HTTP-level via TestClient)

frontend/           React + TypeScript (Vite)
  src/pages/           ExerciseListPage, ExercisePage, RepeatQueuePage
  src/components/      CodeEditor, TrainingBar, Sidebar (Python/Interviews/Coming soon)
  src/services/api.ts    fetch wrapper for the backend

exercises/           Exercise JSON, grouped by content source:
  progressive_python/   Sprint 1's 20 exercises + 2 new nested-loop bridge exercises
  30_days_of_python/     2 exercises adapted from Asabeneh's 30 Days of Python
  42_python_piscine/     19 exercises from the 5 PDF subjects provided this sprint

resources/           Supporting material exercises can reference by path
                     (see resources/README.md for what's here vs. deferred)
```

### Why these choices

- **Raw sqlite3, no ORM.** The goal is learning Python, not building a
  SaaS — a schema + a thin repository is enough for this scope.
- **Exercises as JSON, not hardcoded Python.** Adding an exercise means
  writing a JSON file and re-running `seed.py`, without touching
  application code.
- **Solutions/hidden tests never leave the server.** `GET /exercises/{id}`
  strips `solution`, `hints`, and `hidden_tests` before responding —
  the "don't teach the solution too early" rule is enforced at the API
  boundary, not just in the UI.
- **Two hidden-test modes.** *Function mode* (Sprint 1) calls a
  function and checks its return value. *Script mode* (Sprint 2) runs
  the student's file as a whole program with argv/stdin and checks its
  full stdout — needed because most real 42 Piscine exercises are
  `python script.py arg`, not a function to call.
- **Execution sandbox is intentionally minimal.** Student code runs in
  a separate `python -I` subprocess with a stripped environment, a
  wall-clock timeout, and CPU/memory rlimits — not a real sandbox (no
  seccomp/container/network isolation). See the docstring in
  `app/services/execution_service.py` before exposing this to anyone
  else.

## Setup

Requires [uv](https://docs.astral.sh/uv/), Node.js 18+, and Docker (for
the SQL track's grading database — see below).

```bash
# Backend
cd backend
uv sync
uv run python scripts/seed.py           # Python exercises (exercises/*.json)
uv run python scripts/seed_notes.py     # Python learning notes (notes/*.json)
uv run python scripts/seed_functions.py # Function reference (function_references/*.json)
uv run python scripts/seed_sql.py       # SQL exercises (sql_exercises/*.json)
uv run python scripts/seed_sql_notes.py # SQL learning notes (sql_notes/*.json)
uv run python scripts/seed_exam.py      # Exam question bank (exam_questions/*.json)
uv run pytest                            # full backend test suite should pass
uv run flake8 app scripts tests          # style check (project convention)
uv run uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Re-running any `seed_*.py` script is always safe — each one upserts by
id, so you can re-seed after editing content without wiping progress
data. If the SQLite database ever gets into a weird state during
development, delete `backend/python_gym.db` and re-run every
`seed_*.py` script above from scratch.

Open **http://localhost:5173**. The Vite dev server proxies `/api/*`
to the backend on port 8000 (see `vite.config.ts`), so no CORS setup
is needed beyond what's already in `app/main.py`.

### SQL grading database (Sprint 4)

SQL exercises are graded by running the student's real SQL against a
disposable, local PostgreSQL 16 instance — never a shared/production
database (see the docstring in
`app/services/sql_execution_service.py`). Every submission runs inside
one transaction that's always rolled back, so the fixture data below
never needs re-seeding between individual student submissions — only
when the fixtures themselves change.

```bash
# One-time: start the throwaway Postgres container (skip if it already exists)
docker run --name python-gym-sql \
  -e POSTGRES_PASSWORD=pythongym \
  -e POSTGRES_DB=python_gym_sql \
  -p 55432:5432 \
  -d postgres:16-alpine

# Every time you start work (or after editing resources/sql/fixtures.sql):
docker start python-gym-sql   # if it's stopped
cd backend
uv run python scripts/provision_sql_fixtures.py   # (re)loads resources/sql/fixtures.sql
uv run python scripts/seed_sql.py
uv run python scripts/seed_sql_notes.py
```

`SQL_DATABASE_URL` (default
`postgresql://postgres:pythongym@127.0.0.1:55432/python_gym_sql`) is
overridable via env var if you're pointing at a different local
instance.

## What's in Sprint 2

- **Execution feedback**: the student's own `stdout` is now shown
  cleanly, separate from `stderr`, individual test pass/fail, a result
  value, and execution time — hidden-test internals never leak into
  what the student sees.
- **Script-mode exercises**: `exercise_type: "script"` runs the whole
  file with `sys.argv`/stdin, for exercises structured like the real
  42 Piscine ones.
- **Repeat**: after a pass, "Continue" or "🔁 Repeat later". Repeat is
  its own status (`SOLVED_TO_REPEAT`) — solved, but not mastery, and
  distinct from `FAILED`. A sidebar badge and `/repeat` page surface
  the queue; solving again cleanly clears it.
- **Expanded exercise metadata**: `source`, `track`, `skills`,
  `prerequisites`, `resources`, `validation_profile`, `exercise_type`,
  `exercise_status` (for excluding an exercise from the learning path
  without deleting it).
- **Style checks**: exercises with `validation_profile: "42_piscine"`
  get a flake8 pass/fail alongside — not mixed into hidden-test
  results.
- **Content**: 43 exercises across 3 sources (see below).
- **Sidebar**: Python (Foundations / 30 Days / 42 Piscine), Interviews
  (LeetCode Top Interview 150, shown as Coming soon), and a Coming Soon
  section for future tracks (SQL, Data Science, Mathematics, ML, ML
  Piscine) — static for now, not implemented.

## Content by source

| Source | Count | Notes |
|---|---|---|
| `progressive_python` | 22 | Sprint 1's 20 + 2 new nested-loop bridge exercises |
| `30_days_of_python` | 2 | Adapted from [Asabeneh/30-Days-Of-Python](https://github.com/Asabeneh/30-Days-Of-Python) Day 3 |
| `42_python_piscine` | 19 | From the 5 PDFs provided this sprint (see below) |

Of the 19 42-Piscine exercises, **13 are auto-graded** (hidden tests
verified against their own reference solution through the real
execution engine) and **6 are metadata-only** — included in full
(statement, hints, solution, explanation) but not auto-gradable with
the current engine, because their expected output is inherently
non-deterministic (current date/time, live progress bars, memory
addresses) or their grading shape doesn't fit the current model
(dunder-method side-effect printing). Each one says so in its own
`explanation` field.

**Modules 1–2 of the same Piscine series (Array/NumPy, DataTable/Pandas)
are deliberately not included** — Sprint 2's own spec excludes
NumPy/Pandas this sprint. See `resources/README.md` for the reasoning.

## Adding or editing an exercise

Edit the corresponding file under `exercises/<source>/<id>.json` (or
add a new one following the same shape), then re-run:

```bash
cd backend
uv run python scripts/seed.py
```

Hidden tests come in two shapes:

```json
// function mode (Sprint 1)
{"call": "fn(args)", "expected": "repr(...)"}

// script mode (Sprint 2)
{"args": ["14"], "stdin": null, "expected_stdout": "I'm Even.", "label": "..."}
```

`expected` is compared against `repr()` of the function's return
value; `expected_stdout` is compared against the whole program's
stdout (trailing newline ignored).
