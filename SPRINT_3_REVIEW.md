# Python Gym — Sprint 3 Review

Python Learning Expansion & Learning Foundations. Scope and rationale
are in [`SPRINT_3_PLAN.md`](./SPRINT_3_PLAN.md); this is the mandatory
end-of-sprint report it requires. **Sprint 4 has not been started.**

## 1. Changes

### What changed and why

- **Fixed the real cause of the `progressive_python` reload 500s.**
  `get_service()` in `app/api/exercises.py` and `app/api/progress.py`
  opened a fresh sqlite3 connection per request via a plain
  (non-generator) FastAPI `Depends()` and never closed it. Converted
  both to generator dependencies (`yield ... finally: conn.close()`).
  This was found by three parallel research agents mapping the actual
  bug (a connection leak), which turned out to be distinct from the
  `check_same_thread` cross-thread bug already patched earlier this
  session.
- **Fixed hint leakage.** Hint #3 in `30days-triangle-area.json` and
  `piscine-00-hello.json` was the literal solution code, verbatim. The
  "triangle exercise int()/format('.1f') bug" reported at the start of
  the sprint could not be reproduced — the file has always used
  `float()` consistently (confirmed via git history) — but the hint
  leak was real and is what the report likely meant.
- **Added bilingual (EN/FR) infrastructure**, not full French content.
  Per an explicit scope decision this sprint: build the mechanism
  (nullable `_fr` sibling fields, a fallback expression, a UI language
  toggle) and author real English content now; French text fills in
  incrementally later without doubling this sprint's authoring load.
  Every new exercise has real English content and `null` French fields
  by design — the frontend falls back to English automatically.
- **Added Learning Notes** (new feature): a `learning_notes` table, a
  `NotesRepository`, `GET /api/notes` / `GET /api/notes/{id}`, a seed
  script, and two new frontend pages. Four notes shipped: Lists,
  Dictionaries (mandatory per the brief), Strings, Loops (added because
  they pair directly with this sprint's new content). The remaining
  topics (Functions, Tuples, Sets, Exceptions, Comprehensions, Files,
  Modules, OOP) are Sprint 4 backlog, not silently dropped.
- **Added a basic learning path**: prerequisite ids (stored since
  Sprint 2, never resolved into anything usable) are now resolved into
  `{id, title, solved}` and shown on the exercise page; a new
  `GET /api/exercises/next` endpoint recommends the first unsolved
  exercise in catalog order. Deliberately simple — no scoring, no
  adaptive engine, matching the brief's explicit "not yet" on that.
- **Fixed a pre-existing sidebar mislabel**: `source=progressive_python`
  was labeled "Foundations" with no real Foundations content behind it.
  Added a genuine new `foundations` source (8 exercises: variables,
  types, I/O, operators) and relabeled the existing 28-exercise track
  "Progressive Python."
- **Substantially expanded Python content** (see §2).

### Files added

Backend:
- `backend/app/repositories/notes_repository.py`
- `backend/app/api/notes.py`
- `backend/scripts/seed_notes.py`
- `backend/tests/test_learning_notes.py`, `test_learning_path.py`,
  `test_i18n.py`

Content:
- `exercises/foundations/*.json` (8 files, new directory)
- `exercises/python_gym/*.json` (26 files, new directory)
- `exercises/progressive_python/prog-bridge-{001..006}.json`
- `exercises/30_days_of_python/30days-{string-methods,list-methods,
  dict-practice,function-practice,tuple-unpacking,nested-lists}.json`
- `notes/{lists,dictionaries,strings,loops}.json` (new top-level
  directory, parallel to `exercises/`)

Frontend:
- `frontend/src/i18n/{en.json,fr.json,LocaleContext.tsx}`
- `frontend/src/pages/{LearningNotesListPage,LearningNotePage}.tsx`

Docs:
- `SPRINT_3_PLAN.md`, `SPRINT_3_REVIEW.md` (this file)

### Files modified

Backend: `app/domain/models.py` (French fields, `LearningNote`),
`app/models/database.py` (schema + migration columns, `learning_notes`
table), `app/api/exercises.py` (French fields, `PrerequisiteResponse`,
`/next` route, generator dependency), `app/api/progress.py` (generator
dependency), `app/main.py` (notes router), `app/repositories/
exercise_repository.py` (French columns, `resolve_prerequisites`,
`get_next_unsolved`), `app/services/exercise_service.py` (French
pass-through, hint/solution tuples now include French, new path
methods), `scripts/seed.py` (French field parsing), plus the existing
test files touched to match the new `request_hint`/`reveal_solution`
signatures and `HintResponse` shape (`test_api.py`,
`test_exercise_service.py`, `test_seed_content.py`).

Frontend: `main.tsx` (`LocaleProvider`), `App.tsx` (notes routes),
`components/Sidebar.tsx` + `.css` (Foundations/Python-Gym entries,
relabel, Learning Notes link, language toggle),
`types/exercise.ts` (French fields, `Prerequisite`, note types,
`CONTENT_SOURCES`), `services/api.ts` (`getNextExercise`, `listNotes`,
`getNote`), `pages/ExerciseListPage.tsx` + `.css` ("continue where you
left off", i18n, new module labels), `pages/ExercisePage.tsx`
(prerequisites panel, i18n, French fallback throughout),
`pages/RepeatQueuePage.tsx` (i18n).

Two exercise JSON files edited in place (hint fix only, no other
change): `exercises/30_days_of_python/30days-triangle-area.json`,
`exercises/42_python_piscine/piscine-00-hello.json`.

### Model / API changes

- `Exercise` dataclass: +6 optional French fields, all defaulting to
  `None`/absent so every pre-Sprint-3 exercise stays valid unchanged.
- New `LearningNote` dataclass and `learning_notes` table.
- `exercises` table: +6 nullable columns (`title_fr`, `description_fr`,
  `examples_fr`, `expected_behavior_fr`, `explanation_fr`, `hints_fr`),
  added to both the `CREATE TABLE` (fresh DBs) and the migration dict
  (existing DBs, including the developer's real `python_gym.db`).
- `POST /{id}/hint` now returns `{hint, hint_fr}` instead of `{hint}` —
  a breaking response-shape change, same category as Sprint 2's
  `/submit` change; only this repo's own frontend consumes it.
- `POST /{id}/solution` now returns `explanation_fr` in addition to
  `solution`/`explanation`.
- `GET /{id}` now returns `prerequisites` as `[{id, title, solved}]`
  objects instead of raw id strings — also breaking, same caveat.
- New `GET /api/exercises/next` and `GET /api/notes`,
  `GET /api/notes/{id}`.
- `ExerciseService.request_hint()` now returns `(hint, hint_fr)`;
  `reveal_solution()` now returns `(solution, explanation,
  explanation_fr)`.

## 2. Content

| Addition | Source | Count | Module breakdown |
|---|---|---|---|
| Foundations | `foundations` (new) | 8 | variables, types, input_output, operators (2 each) |
| Core Python gaps | `python_gym` (new) | 17 | strings (3), tuples (2), sets (2), dictionaries (3), functions (3), scope (2), exceptions (2) |
| Intermediate Python | `python_gym` | 9 | comprehensions (2), files (2), modules (1), oop (2), iterators_generators (2) |
| Progressive Python bridge | `progressive_python` | +6 | loop+condition, loop+list, loop+dict, strings, nested structures, functions-as-values |
| 30 Days of Python | `30_days_of_python` | +6 | strings, lists, dicts, functions, tuples, nested lists |
| **Total new** | | **46** | |

Catalog: **43 → 89 exercises**. Every new exercise has 3 hints (last
hint nudges, never pastes the solution), real hidden tests, and an
explanation. All 46 were authored by 6 parallel content-authoring
agents against a strict shared schema, each given pre-computed exact
expected values (I traced every test case by hand before delegating)
to eliminate the class of bug where an "expected" value is simply
wrong. See §3 for how this was verified.

**Learning notes**: Lists, Dictionaries, Strings, Loops (4). Each has
explanation, syntax, examples, common mistakes, a mini exercise, and
links to real practice exercises — cross-checked against the actual
seeded catalog (see `test_related_exercise_ids_resolve_to_real_
exercises`). Functions, Tuples, Sets, Exceptions, Comprehensions,
Files, Modules, OOP notes are Sprint 4 backlog.

**Resources**: no new files added under `resources/` this sprint — no
new exercise had a genuine need for a support file beyond what already
exists (`python/30-days/03_day_operators.md`, still referenced by the
original two 30-Days exercises).

**Excluded exercises**: the Piscine-0 "compression" exercise still does
not exist as real content — confirmed again this sprint (only a
synthetic test fixture exercises the `exercise_status="excluded"`
mechanism). Nothing to newly exclude; stays backlog until a real
PDF/spec is provided.

**42 Python Piscine**: unchanged at 19 exercises (capped this sprint,
per your call — no new PDFs).

## 3. Tests

**93 tests pass** (`uv run pytest`), up from 61. `uv run flake8 app
scripts tests` is clean.

New test files: `test_learning_notes.py` (13 tests — repository,
HTTP routes, seed-loading of all 4 real note files, and a
related-exercise-id integrity check against the real catalog),
`test_learning_path.py` (11 tests — prerequisite resolution incl. a
dangling-reference case, `get_next_unsolved` incl. exclusion/source
filtering, both over the repository and over HTTP), `test_i18n.py` (9
tests — French round-trip through storage, null-fallback behavior,
and the same over HTTP for exercise detail/list/hint/solution).

Extended existing files: `test_seed_content.py` (`EXPECTED_SOURCES` now
includes `foundations`/`python_gym`; added a catalog-size regression
test asserting per-source minimums so a future refactor can't silently
lose content), `test_api.py` (updated `HintResponse` shape assertion;
added `test_repeated_source_filtered_requests_do_not_leak_connections`
— 50 requests to the exact endpoint from the bug report, all asserted
200), `test_exercise_service.py` (updated for the new
`request_hint`/`reveal_solution` tuple returns).

**Content QA beyond the test suite**: every one of the 89 exercises'
`solution` was actually executed against its own `hidden_tests` via the
real `execution_service.run_submission` (not just the pytest suite) —
a one-off script mirroring exactly how a student submission is graded.
All 46 new exercises passed cleanly. 9 pre-existing Sprint 2
`42_python_piscine` exercises fail this check (see §5, Problems) —
confirmed via `git diff` to be completely untouched by this sprint, a
pre-existing characteristic of "metadata-only" function-mode exercises
with empty `hidden_tests`, not a Sprint 3 regression.

**Frontend**: `npx tsc -b --noEmit` clean, run twice (after backend
type changes and again after all page edits). No frontend test runner
exists in this repo and adding one was out of scope.

**Manual end-to-end verification**: both dev servers started fresh;
hit `/api/exercises?source=foundations` (8 results), `/api/notes` (4),
`/api/notes/lists` (full note incl. related exercises),
`/api/exercises/next?source=python_gym`, prerequisite resolution on
`prog-bridge-001` (resolves to `loop-005`, unsolved), and 20 more
requests to `?source=progressive_python` (all 200). Backend log showed
zero 4xx/5xx across the whole session, including apparent live manual
browsing through every sidebar source during this session.

## 4. Regression check

**Connection leak (P0 fix)**

- Before: `get_service()` opened a connection per request, never
  closed it. Repeated requests to any endpoint accumulated open
  connections/file descriptors.
- After: generator dependency, `conn.close()` in `finally`.
- Why: found by tracing the actual reported symptom
  ("repeated reloads + 500 on `progressive_python`") instead of
  assuming it was the already-patched thread-safety bug.
- Risk: none identified — connections were already request-scoped
  (never shared across concurrent requests), so closing them at the
  end of the request has no behavioral side effect. Verified with 50
  and then 20 more back-to-back requests, all 200.

**Hint response shape**

- Before: `{"hint": str}`.
- After: `{"hint": str, "hint_fr": str | None}`.
- Why: French hints need to reach the frontend somehow; adding a
  sibling field keeps the English contract unchanged for any other
  consumer.
- Risk: breaking change for any external consumer of this endpoint.
  None exists outside this repo's own frontend, which was updated in
  the same change.

**Prerequisites shape**

- Before: `prerequisites: string[]` (raw ids, unusable by the UI).
- After: `prerequisites: {id, title, solved}[]`.
- Why: this is the entire point of "basic learning path" — raw ids
  were dead data.
- Risk: same breaking-change caveat as above, same mitigation.

**Sprint 1 & 2 functionality explicitly re-verified**: hint reveal
order, solution reveal, submission pass/fail, repeat-queue behavior
(mark/unmark, `SOLVED_TO_REPEAT` staying distinct from `MASTERED`),
mastery-after-two-clean-solves, style checking for `42_piscine`
profile, script-mode vs. function-mode grading, and exclusion filtering
— all covered by the pre-existing test files, all still passing
unmodified except for the two files whose assertions had to change to
match the new (intentional) response shapes.

## 5. Problems

- **9 pre-existing `42_python_piscine` exercises can't "pass" their own
  solution** under the grader's `tests_total > 0` requirement, because
  they were deliberately seeded with empty `hidden_tests` (Sprint 2's
  answer to non-deterministic output — dates, memory addresses, set
  ordering). This is unrelated to Sprint 3 and was already flagged in
  `SPRINT_2_REVIEW.md` as a proposed fix ("pattern-based
  `expected_stdout`") that didn't happen this sprint either — still
  open.
- **French content is real but thin.** Every new exercise/note has
  working `_fr` infrastructure and a language toggle, but zero actual
  French translations exist yet (by design this sprint) — every French
  field is currently `null` and falls back to English. Sprint 4 (or a
  dedicated translation pass) needs to actually fill these in for the
  experience to be bilingual in practice, not just in the schema.
- **Learning notes cover 4 of ~12 candidate topics.** Functions,
  Tuples, Sets, Exceptions, Comprehensions, Files, Modules, OOP have no
  note yet, even though `python_gym` exercises for all of them now
  exist.
- **The Piscine-0 compression exercise is still unsourced** — third
  sprint in a row this stays backlog; no PDF/spec has ever been
  provided for it.
- **`related_exercise_ids` on a note render as raw ids in the
  frontend** (e.g. `list-001`), not resolved titles — a real exercise
  title lookup was out of scope for this pass; functional but not
  polished.
- **`PYTHONHASHSEED` is still an inert no-op** in
  `execution_service.py` (flagged in Sprint 2, not touched this
  sprint either — real fix or removal still pending).
- **Directory layout inconsistency partially addressed, not
  resolved.** `python_gym`/`foundations` are new well-organized
  directories, but the Sprint 1 `conditions/`/`for_loops/`/`lists/`
  directories (which all default to `source=progressive_python`)
  remain unreconciled with the newer `exercises/<source>/` convention,
  as flagged in `SPRINT_2_REVIEW.md`.

## 6. Proposed Sprint 4 scope (not started)

Per `SPRINT_3_PLAN.md`: **SQL Foundations + Progressive SQL + SQL
Challenges**, and **Interview Foundations + Python Interview Practice**
(prep for LeetCode Top Interview 150), reusing the exact same
`track`/`source`/`concepts`/`skills`/`prerequisites`/`difficulty`/
`attempts`/`progress` architecture — no new engine needed, the Sprint 3
learning-path/i18n/notes plumbing already generalizes past Python.
Concretely I'd suggest, in priority order: (1) a real French
translation pass over this sprint's 46 exercises and 4 notes before
adding more untranslated content, (2) the remaining 8 learning notes,
(3) SQL Foundations track using the same content-JSON + seed-script
pattern, (4) Interview Foundations. Sprint 4 should not start until you
confirm this scope.
