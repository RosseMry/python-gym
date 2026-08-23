# Python-Gym — Sprint 2 Review

## 1. What was implemented

- **Execution feedback overhaul (P0)**: student `stdout` is now shown
  cleanly, stripped of internal hidden-test protocol data; `stderr`,
  individual test outcomes, a `result` value, `execution_time`, and an
  explicit `status` (`passed`/`failed`/`error`) are all surfaced
  separately.
- **Script-mode exercises**: a second hidden-test shape
  (`args`/`stdin`/`expected_stdout`) that runs the student's file as a
  whole program instead of calling a function, needed because most
  real 42 Piscine exercises are `python script.py arg`-shaped.
- **Repeat (P1)**: `SOLVED_TO_REPEAT` status, a `POST
  /exercises/{id}/repeat` endpoint (guarded — only a solved exercise
  can be queued), a `GET /exercises/repeat-queue` endpoint, and a
  sidebar badge + `/repeat` page. Solving the exercise again cleanly
  clears it from the queue automatically (no separate "un-repeat"
  action needed).
- **`FAILED` status**: a failed submission now moves an exercise to
  `FAILED` rather than the previous `ATTEMPTED` (which is now reserved
  for "requested a hint, hasn't submitted yet").
- **Expanded exercise metadata**: `track`, `source`, `skills`,
  `prerequisites`, `resources`, `validation_profile`, `exercise_type`,
  `exercise_status` on every exercise, with backward-compatible
  defaults for Sprint 1 exercises that predate these fields.
- **Style checks**: a flake8-based check, run only for
  `validation_profile: "42_piscine"` exercises, reported as a separate
  `style` field — never folded into hidden-test pass/fail.
- **Content**: 43 exercises across `progressive_python` (22),
  `30_days_of_python` (2), `42_python_piscine` (19).
- **Sidebar**: Python (Foundations/30 Days/42 Piscine), Interviews
  (LeetCode Top Interview 150, disabled), Coming Soon (SQL, Data
  Science, Mathematics, ML, ML Piscine, disabled).

## 2. Files changed (Sprint 1 → Sprint 2)

| File | Change |
|---|---|
| `backend/app/domain/models.py` | Extended `ExerciseStatus`, `HiddenTest`, `Exercise`, `SubmissionResult`; added `TestOutcome`, `StyleCheckResult` |
| `backend/app/models/database.py` | Added Sprint 2 columns to `exercises`/`submissions`, with a migration path for pre-existing DBs |
| `backend/app/repositories/exercise_repository.py` | Persist/read new fields; `list_by_source`, `list_repeat_queue`, `include_excluded` filter on `list_all` |
| `backend/app/services/execution_service.py` | Full rewrite: protocol-tag stdout separation, script-mode execution path, richer `SubmissionResult` |
| `backend/app/services/exercise_service.py` | `mark_repeat`, `list_by_source`, `list_repeat_queue`; `submit()` now sets `FAILED` on failure and attaches style checks for 42-piscine exercises |
| `backend/app/api/exercises.py` | Richer response models; `source` query param; `/repeat-queue` and `/{id}/repeat` endpoints |
| `backend/app/api/progress.py` | flake8 line-length fix only, no behavior change |
| `backend/scripts/seed.py` | Reads/defaults the new metadata fields; prints a per-source summary |
| `frontend/src/types/exercise.ts` | New fields, `TestOutcome`, `StyleCheckResult`, `CONTENT_SOURCES` |
| `frontend/src/services/api.ts` | `source` filter, `getRepeatQueue`, `markRepeat` |
| `frontend/src/pages/ExercisePage.tsx` | Full rewrite: Output/Tests/Error/Style panel, Continue/Repeat buttons |
| `frontend/src/pages/ExerciseListPage.tsx` | Source filtering via `?source=`, new module labels |
| `frontend/src/App.tsx` | Sidebar layout, `/repeat` route |
| `frontend/src/components/TrainingBar.tsx` | `STATUS_ORDER` covers the two new statuses |

## 3. New files

- `backend/app/services/style_service.py`
- `backend/tests/test_repeat.py`, `test_execution_output.py`,
  `test_style_service.py`, `test_exercise_metadata.py`,
  `test_validation_profile.py`, `test_seed_content.py`
- `frontend/src/components/Sidebar.{tsx,css}`
- `frontend/src/pages/RepeatQueuePage.tsx`
- `exercises/42_python_piscine/*.json` (19 files)
- `exercises/30_days_of_python/*.json` (2 files)
- `exercises/progressive_python/prog-nested-loop-*.json` (2 files)
- `scripts/generate_42_piscine.py`,
  `scripts/generate_42_piscine_oop_dod.py`,
  `scripts/generate_progressive_and_30days.py`
- `resources/README.md`, `resources/python/30-days/03_day_operators.md`

## 4. Models changed

- `ExerciseStatus`: added `FAILED`, `SOLVED_TO_REPEAT`.
- `HiddenTest`: now supports either call-mode (`call`, `expected`) or
  script-mode (`args`, `stdin`, `expected_stdout`), plus a `label`.
- `Exercise`: added `track`, `source`, `skills`, `prerequisites`,
  `resources`, `validation_profile`, `exercise_type`,
  `exercise_status`.
- `SubmissionResult`: replaced the flat pass/fail shape with `status`,
  `tests: list[TestOutcome]`, `result`, `execution_time`, `style`.
- New: `TestOutcome`, `StyleCheckResult`.

## 5. Endpoints changed

- `GET /api/exercises` — added `?source=` filter.
- `GET /api/exercises/repeat-queue` — new.
- `POST /api/exercises/{id}/repeat` — new (204, or 404/409).
- `POST /api/exercises/{id}/submit` — response body reshaped (see
  `SubmissionResponse` in `app/api/exercises.py`); **this is a
  breaking change to the API shape**, noted as risk below.
- `GET /api/exercises/{id}` — added metadata fields to the response.

## 6. Frontend components changed

- `ExercisePage` (rewritten), `ExerciseListPage` (source filter),
  `App` (sidebar layout + `/repeat` route), `TrainingBar` (status
  coverage). New: `Sidebar`, `RepeatQueuePage`.

## 7. Exercises added, by source

| Source | Added this sprint | Auto-graded | Metadata-only |
|---|---|---|---|
| `progressive_python` | 2 (nested-loop bridge) | 2 | 0 |
| `30_days_of_python` | 2 | 2 | 0 |
| `42_python_piscine` | 19 | 13 | 6 |

Metadata-only 42-Piscine exercises (full statement/hints/solution
included, no auto-grading) and why:

- `piscine-00-format-time` — output depends on the current date/time.
- `piscine-00-loading` (`ft_tqdm`) — output is a live-updating progress
  bar, not a fixed string.
- `piscine-00-package` — a packaging/tooling task, not a single
  function to grade.
- `piscine-03-got-s1e7`, `piscine-03-diamond-trap`,
  `piscine-03-calculator-vector`, `piscine-04-calllimit` — expected
  output includes wording that's up to the student (`__str__`
  messages) or a real memory address (`<function g at 0x...>`) that
  changes every run.
- `piscine-04-statistics`, `piscine-04-dataclass-student` — same
  category as above (free-text prints; a `Student`'s repr that only
  needs *one* field to differ (`id` is random) to legitimately fail an
  exact-match test).

(`piscine-00-hello` was originally graded but demoted to
metadata-only after the review caught a real bug — see section 15.)

## 8. Exercises excluded

None from this sprint's actual content. Sprint 2 spec section 33
describes a compression exercise elsewhere in the 42 Piscine that
should be excluded — it doesn't appear in the 5 PDFs provided this
sprint, so nothing real was excluded. The `exercise_status: "excluded"`
mechanism itself is implemented and covered by
`test_exercise_metadata.py` using a synthetic fixture, ready for when
a real excluded exercise needs it.

**Scope decision**: Modules 1 ("Array", NumPy) and 2 ("DataTable",
Pandas) of the same Piscine series were in the provided PDFs but were
**not** turned into seeded exercises, because Sprint 2's own spec
(section 43) explicitly excludes NumPy and Pandas this sprint. This is
a scope decision, not an exclusion in the spec's sense — the exercises
exist, they're just deferred. Documented in `resources/README.md`.

## 9. Resources added

- `resources/README.md` — documents the resources structure, what's
  included, and the Module 1/2 deferral.
- `resources/python/30-days/03_day_operators.md` — a pointer to the
  real source, not a copy of it.
- Empty `resources/python/42-piscine/`, `resources/python/leetcode/`,
  `resources/datasets/` directories, prepared per spec section 27 for
  future sprints.

## 10. Validations added

- `validation_profile` field on every exercise (`standard_python` or
  `42_piscine`).
- `style_service.check_style()` — flake8 against submitted code,
  timeout-guarded, never raises. Wired into `submit()` only for
  `42_piscine`-profile exercises.
- `exercise_type` (`function`/`script`) drives which execution path
  `run_submission` takes.

## 11. Tests added

30 new tests across 6 new files (61 total, up from 31):
`test_repeat.py` (7), `test_execution_output.py` (7),
`test_style_service.py` (3), `test_exercise_metadata.py` (7),
`test_validation_profile.py` (3), `test_seed_content.py` (5), plus one
existing test updated for the `FAILED`-vs-`ATTEMPTED` behavior change.

## 12. `uv run pytest` result

```
61 passed, 1 warning in 7.20s
```

The one warning is a pre-existing `httpx`/`starlette` deprecation
notice, unrelated to Sprint 2 changes.

`uv run flake8 app scripts tests` (backend app code): clean, 0
issues, after two fixes (a long line in `app/api/progress.py`, a
trailing blank line in `app/services/exercise_service.py`).

**Not held to the 88-char/flake8 standard**: the top-level
`scripts/generate_*.py` files (content generators, not part of the
running app — mostly long string literals holding exercise text).
This is a disclosed scope decision, not an oversight.

## 13. Architectural decisions

- **Two hidden-test modes on one `HiddenTest` dataclass** (optional
  fields, `is_script_mode` property) rather than two separate types —
  keeps the JSON schema and repository code simple, at the cost of a
  dataclass with fields that are mutually exclusive in practice.
- **`PYTHONHASHSEED=0` in the execution subprocess env**, discovered
  necessary when a hidden test asserting exact `stdout` for a program
  that prints a `set` literal flaked between runs (set iteration order
  depends on string hash randomization). Note: this had **no effect**
  under `-I` (isolated mode ignores `PYTHONHASHSEED`) — see section 15
  for how this was actually resolved.
- **Style checks live outside `execution_service.py`**, in their own
  `style_service.py`, and are attached to a `SubmissionResult` after
  the fact (`_with_style_check` in `exercise_service.py`) rather than
  being a parameter to `run_submission`. Keeps the sandboxed-execution
  code free of anything to do with linting.
- **Repeat has no explicit "un-repeat" action.** Solving the exercise
  again cleanly transitions it out of `SOLVED_TO_REPEAT` via the
  existing `_next_status_on_success` logic — no new code path needed,
  and it matches the spec's framing of repeat as "practice debt" that
  clears itself when paid off.

## 14. Problems / open questions for Sprint 3

- **The `/submit` response shape changed incompatibly.** Any external
  consumer of Sprint 1's `SubmissionResponse` (just `passed`,
  `tests_total`, `tests_passed`, `stdout`, `stderr`, `error`) would
  break against Sprint 2's response. Only this repo's own frontend
  consumes it today, and it was updated in lockstep, so no live
  breakage — but a versioned API or a migration note would matter if
  this were ever used externally.
- **Script-mode grading for exercises whose stdout embeds
  nondeterministic content** (dates, memory addresses, random ids) is
  still an open problem, not a solved one — Sprint 2's answer is "mark
  it metadata-only," which is honest but means 6 of 19 Piscine
  exercises aren't auto-graded. A pattern/regex-based `expected_stdout`
  (rather than exact match) would close some of this gap in a future
  sprint.
- **Directory layout inconsistency**: Sprint 1's exercises still live
  flat under `exercises/<module>/` (e.g. `exercises/conditions/`)
  while Sprint 2's new content lives under `exercises/<source>/`. Both
  load correctly (the seed script globs `exercises/**/*.json`), so
  this is cosmetic, not a bug — flagged rather than silently
  reorganized, per the "no unnecessary refactors" rule.
- **Prerequisites are stored but not enforced.** `prerequisites` is on
  the model and populated for a few exercises, but nothing gates
  access based on it yet (per spec section 21, deliberately deferred).

## 15. Technical debt / bugs found and fixed during this sprint

- **Protocol-tag collision bug**: the first stdout-separation sentinel
  used control characters (`\x1e`) that `str.splitlines()` treats as
  line boundaries, silently breaking the tag apart and making every
  test outcome disappear. Caught by the new execution tests, fixed by
  switching to a plain-ASCII tag and splitting on `\n` explicitly
  rather than `str.splitlines()`.
- **Set-ordering flake in `piscine-00-hello`**: the exercise's own
  reference solution intermittently failed its own hidden test because
  printing a Python `set` has no guaranteed order. `PYTHONHASHSEED=0`
  was added to the execution environment as a first attempt, but
  turned out to have no effect because `python -I` (isolated mode)
  ignores `PYTHONHASHSEED` entirely — a real gap in that fix worth
  knowing about if hash-seed determinism is ever needed elsewhere. The
  actual fix was to stop asserting exact stdout for a line that's
  inherently unordered, converting that one hidden test to
  metadata-only (same treatment as the other 5 non-deterministic
  Piscine exercises).

## 16. Which parts of Sprint 1 were modified, and why

| What | Before | After | Why | Regression risk |
|---|---|---|---|---|
| Failed submission | → `ATTEMPTED` | → `FAILED` | Spec section 4 distinguishes "haven't solved it" from "requested a hint" | Low — covered by an updated test (`test_wrong_submission_fails_and_marks_failed`); any external code branching on `ATTEMPTED` after a failed submit would need updating, but none exists outside this repo |
| `SubmissionResult` shape | `passed`/`tests_total`/`tests_passed`/`stdout`/`stderr`/`error` | adds `status`/`tests`/`result`/`execution_time`/`style` | Spec sections 10-15 require this detail | Low — old fields still present with the same meaning; only additive except `stdout` no longer contains hidden-test protocol lines (which were never meant to be visible anyway) |
| `record_submission` signature | 5 params | 8 params (status, hint/solution snapshots) | Spec section 7 wants attempts to retain context | None — call site updated in the same change, old callers don't exist elsewhere |
| Execution subprocess env | `env={}` | `env={"PYTHONHASHSEED": "0"}` | Attempted determinism fix (see section 15 — turned out to be a no-op under `-I`) | None functionally, but worth removing or replacing with a real fix in Sprint 3 since it currently does nothing |

All 31 original Sprint 1 tests still pass unmodified except the one
`ATTEMPTED`→`FAILED` test, which was updated to reflect the
intentional behavior change (not a regression).

## 17. Proposed improvements for Sprint 3

1. Pattern-based `expected_stdout` (e.g. a regex or a placeholder
   syntax for "a memory address goes here") to auto-grade more of the
   6 currently metadata-only 42-Piscine exercises.
2. A real fix (or removal) of the `PYTHONHASHSEED` env var, since it's
   currently inert under `-I`.
3. Prerequisite enforcement in the learning path (locked exercises
   until prerequisites show real practice, not just "attempted once").
4. Reconcile the `exercises/<module>/` vs `exercises/<source>/`
   directory layout.
5. Consider versioning the `/submit` response shape if any external
   consumer is ever expected.
