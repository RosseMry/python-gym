# Python Gym — Sprint 1 (MVP)

A local practice platform to build Python fluency for Machine Learning,
by making you write code from scratch instead of copying it.

This is **Sprint 1** only, as scoped in the original spec: exercise
engine, 20 exercises (conditions, for loops, lists), a code editor,
submit + hidden-test grading, hints, and basic status tracking.
Sprints 2–5 (spaced repetition, dashboards, ML modules, mastery
polish) are intentionally not built yet.

## Architecture

```
backend/            FastAPI + SQLite, layered:
  app/api/           HTTP routes (thin — parse request, call service, shape response)
  app/domain/         Plain dataclasses: Exercise, ProgressEntry, SubmissionResult
  app/services/        Business rules: hint sequencing, mastery rules, sandboxed execution
  app/repositories/     SQLite persistence, no business logic
  app/models/database.py  Schema + connection
  scripts/seed.py       Loads exercises/*.json into SQLite
  tests/               pytest suite (unit + HTTP-level via TestClient)

frontend/           React + TypeScript (Vite)
  src/pages/           ExerciseListPage, ExercisePage (the hint/attempt/solution flow)
  src/components/      CodeEditor, TrainingBar (the module-progress visual)
  src/services/api.ts    fetch wrapper for the backend

exercises/           The 20 Sprint 1 exercises as JSON (source of truth,
                     re-seedable any time — editing a JSON file and
                     re-running scripts/seed.py updates the DB)
```

### Why these choices

- **Raw sqlite3, no ORM.** The goal is learning Python, not building a
  SaaS — a schema + a thin repository is enough for this scope.
- **Exercises as JSON, not hardcoded Python.** Adding exercise #21
  later means writing a JSON file and re-running `seed.py`, without
  touching application code.
- **Solutions/hidden tests never leave the server.** `GET /exercises/{id}`
  strips `solution`, `hints`, and `hidden_tests` before responding —
  the "don't teach the solution too early" rule is enforced at the API
  boundary, not just in the UI.
- **Execution sandbox is intentionally minimal for the MVP.** Student
  code runs in a separate `python -I` subprocess with a stripped
  environment, a wall-clock timeout, and CPU/memory rlimits — not a
  real sandbox (no seccomp/container/network isolation). This is fine
  for solo local use; see the docstring in
  `app/services/execution_service.py` before exposing this to anyone
  else.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and Node.js 18+.

```bash
# Backend
cd backend
uv sync
uv run python scripts/seed.py     # loads the 20 exercises into SQLite
uv run pytest                      # 31 tests should pass
uv run uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Open **http://localhost:5173**. The Vite dev server proxies `/api/*`
to the backend on port 8000 (see `vite.config.ts`), so no CORS setup
is needed beyond what's already in `app/main.py`.

## What's included in Sprint 1

- 20 exercises: 5 conditions, 10 for-loops (following the level 1–8
  progression from the spec: read → write → accumulate → count →
  filter → transform → enumerate), 5 lists.
- Each exercise: statement, examples, starter code, 3 hints, hidden
  tests, solution, explanation, tagged concepts.
- Submit → sandboxed execution → pass/fail + partial test results.
- Hint button reveals one hint at a time, tracked server-side.
- Explicit "reveal solution" (behind a `<details>` disclosure, not a
  prominent button, per the spec's anti-copy philosophy) — revealing
  it marks that exercise as `SOLVED_WITH_HINT` even if later resubmitted
  correctly, so it can't silently count as full mastery.
- "Explain your code" free-text box after a pass, saved to the DB.
- Basic status model: `NEW → ATTEMPTED → SOLVED_WITH_HINT / SOLVED →
  MASTERED` (two clean solves = mastered).
- `TrainingBar`: a small distinct progress visual per module (each
  exercise is a "plate" on a bar — outline when new, filled and taller
  as it's solved/mastered).

## Not yet built (future sprints, per the spec)

- Sprint 2: attempts/timing analytics UI, difficulty gating.
- Sprint 3: dictionaries, strings, functions modules; spaced repetition.
- Sprint 4: NumPy + ML exercises, linear-regression training module.
- Sprint 5: fluency dashboard, full mastery logic, polish.

## Adding or editing an exercise

Edit the corresponding file under `exercises/<module>/<id>.json` (or
add a new one following the same shape), then re-run:

```bash
cd backend
uv run python scripts/seed.py
```

`hidden_tests` entries are `{"call": "fn(args)", "expected": "repr(...)"}`
pairs — `expected` is compared against `repr()` of the actual return
value, so strings need their own quotes, e.g. `"'positive'"`.
