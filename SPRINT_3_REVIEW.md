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

---

## Addendum — Sprint 3 Architecture Correction

You corrected the information architecture and completeness of the
above pass with a follow-up spec. This addendum documents that
correction; the sections above are left as originally written (history,
not retroactively edited).

### What changed and why

- **Piscine reconciled against the real repo, not PDFs I no longer had.**
  You pointed me at `github.com/zstenger93/python_piscine` as a
  substitute source. File-by-file reconciliation found the real catalog
  is **29 exercises** (Module 0: 10, Module 1: 6, Module 2: 4, Module 3:
  5, Module 4: 4) — and that the 19 already seeded (Modules 0/3/4) were
  **already fully correct**, matching the real repo exactly. The actual
  gap was Modules 1 (Array) and 2 (DataTable), both requiring NumPy/
  Pandas. Added all 10 as new `Exercise` rows with real titles/
  descriptions and a new `exercise_status = "locked"` (distinct from
  `"excluded"`: visible in the catalog, greyed out, never recommended by
  `/exercises/next`, never fabricated as gradable). Catalog now
  represents the full real 29.
- **30 Days of Python: real complete import, not ~10 invented-in-spirit
  exercises.** Real per-day counts (fetched from the source repo's raw
  markdown, not estimated) turned out far larger than expected — Day 5
  alone has 31 exercises (27 Level 1 + 4 Level 2 — the real count is 4,
  not the 3 first estimated). You scoped this to Days 5-8 (Lists/Tuples/
  Sets/Dictionaries) for this pass, Days 1-4 excluded (covered by
  Foundations already), Days 22-30 locked (need live network/a database/
  a web server — don't fit the local function/script grading model; Day
  30 has no exercises and is omitted). **69 real exercises imported**:
  Lists 31, Tuples 12, Sets 15, Dictionaries 11 — every one's
  description preserves the real source instruction text, with a
  clearly separated `"Python-Gym adaptation: ..."` line only where a
  callable signature had to be invented to make it hidden-test-gradable.
  Days 9-21 are explicit backlog for future passes.
- **Recategorized 6 previously-mislabeled exercises.** The prior pass's
  `30days-string-methods`/`-list-methods`/`-dict-practice`/
  `-function-practice`/`-tuple-unpacking`/`-nested-lists` were invented,
  theme-inspired content, not real imports — their own authoring
  report said so. Now that real Day 5/6/8 content exists, keeping them
  labeled `source="30_days_of_python"` would misrepresent them as
  sourced. Moved to `exercises/python_gym/` with a `pg-` id prefix and
  `source="python_gym"` — same content, honestly labeled. Fixed the
  stale references this broke in `notes/lists.json`, `strings.json`,
  `dictionaries.json`.
- **Sidebar restructured**: Foundations/Progressive Python/Python-Gym
  are no longer 3 separate nav items — they're one "Progressive →
  Foundations" link fetching all three sources in one request (new
  comma-separated `source` query param, `list_by_source` now does
  `WHERE source IN (...)`). "Progressive → 30 Days of Python" is now its
  own dedicated page (`/thirty-days`), not a source filter — Day 01-30
  accordion structure, populated days expandable, locked days (22-29)
  shown muted with a reason, not-yet-imported days (1-4, 9-21) shown
  structurally per the spec but without fabricated content. Added a
  disabled "Python Exam" entry completing the Progressive → Piscine →
  Exam path visually.
- **Status split**: `SOLVED_WITH_HINT` used to mean both "used a hint"
  and "revealed the solution." Split into `SOLVED_WITH_HINT` (hint used)
  and new `SOLVED_AFTER_SOLUTION` (solution revealed) — different
  signals for the future adaptive/exam system. Both still count as
  "solved" for repeat-eligibility and prerequisite resolution; neither
  counts toward mastery, unchanged from before.
- **Learning Notes redesigned**: key-idea card (`--focus` accent),
  syntax/examples kept as-is, a warning card for common mistakes
  (`--danger` accent), a "try this" card for the mini exercise
  (`--success` accent, previously an unused token pair) — replacing the
  flat stacked-panel layout.

### Files added

Backend: `backend/tests/test_locked_and_multisource.py`.

Content: 10 locked Piscine exercises
(`exercises/42_python_piscine/locked/*.json`); 69 real Day 5-8 imports
(`exercises/30_days_of_python/30days-d0{5,6,7,8}-*.json`).

Frontend: `pages/ThirtyDaysPage.tsx` + `.css`, `pages/LearningNote.css`.

### Files modified

Backend: `app/domain/models.py` (`day`/`level` fields,
`SOLVED_AFTER_SOLUTION`, `"locked"` status documented), `app/models/
database.py` (schema + migration columns for `day`/`level`),
`app/repositories/exercise_repository.py` (`day`/`level` round-trip,
multi-source `list_by_source`, `locked` excluded from
`get_next_unsolved`, both `solved_family` tuples updated),
`app/services/exercise_service.py` (`_SOLVED_FAMILY`,
`_next_status_on_success` split, `day`/`level` pass-through),
`app/api/exercises.py` (`day`/`level`/`exercise_status` exposed on both
response schemas), `scripts/seed.py` (parse `day`/`level`). Existing
tests updated for the status split (`test_exercise_service.py`,
`test_exercise_repository.py`) and the new real counts
(`test_seed_content.py`).

Frontend: `components/Sidebar.tsx` + `.css` (Progressive/Piscine/Exam
restructure), `components/TrainingBar.tsx` + `.css` (status split),
`pages/ExerciseListPage.tsx` + `.css` (locked-card rendering, merged-
source heading, new module labels), `pages/LearningNotePage.tsx` (card
classes), `types/exercise.ts` (`day`/`level`/`exercise_status`,
`SOLVED_AFTER_SOLUTION`), `App.tsx` (`/thirty-days` route),
`resources/README.md` (locked-exercise documentation).

6 exercise files moved + edited (source recategorization, see above).
2 note files edited (stale reference fixes).

### Content

| Addition | Count |
|---|---|
| Piscine locked entries (Module 1 + 2) | 10 |
| 30 Days real imports (Days 5-8) | 69 (Lists 31, Tuples 12, Sets 15, Dicts 11) |
| Recategorized (30-days-inspired → python_gym) | 6 |
| **Catalog total** | **168** (up from 89) |

### Tests

**108 tests pass** (`uv run pytest`), up from 93. `uv run flake8 app
scripts tests` clean. New: `test_locked_and_multisource.py` (10 tests —
day/level round-trip, locked visible-but-never-recommended, comma-
separated source merge, both at repository and HTTP layers). Extended:
`test_seed_content.py` (exact Piscine=29 assertion, 10-locked-exercises
check, exact per-day counts for Days 5-8 as a regression guard against
losing real content in a future refactor).

**Content QA**: same solution-vs-own-hidden-tests script as the
original Sprint 3 pass, re-run against the full 168-exercise catalog.
All 69 new imports and all 10 locked entries behave exactly as
expected (locked entries correctly fail — they have no solution by
design); the same 9 pre-existing Sprint 2 metadata-only exercises still
fail for the same pre-existing reason (confirmed via `git diff`
untouched).

### Regression check

- **`get_next_unsolved` excluding locked exercises**: before, only
  `exercise_status != 'excluded'` was checked, so a locked exercise
  (once seeded) would have been recommended as "next" despite having no
  solution — a real bug that would have surfaced immediately once
  Module 1/2 entries existed. Fixed by excluding `'locked'` too, before
  any user could hit it (caught in review, not production).
  Verified: 10 consecutive calls to `/exercises/next?source=
  42_python_piscine` never returned a locked id.
- **Status split**: verified both old assertions (hint → `SOLVED_WITH_
  HINT`) and new (reveal → `SOLVED_AFTER_SOLUTION`) pass, and that
  `SOLVED_AFTER_SOLUTION` is still repeat-eligible (new test).
- **Merged-source connection/leak behavior**: hammered
  `?source=foundations,progressive_python,python_gym` 15x back-to-back
  post-restart — same technique used to verify the original Sprint 3
  connection-leak fix — all 200s, confirming the new `IN (...)` query
  path didn't reintroduce it.
- Sprint 1/2/3 functionality spot-checked again after the restructure:
  hint/solution reveal, submit pass/fail, repeat queue, existing
  Learning Notes API, all still 200 with no backend errors across the
  full smoke-test session (confirmed via log grep for 4xx/5xx — none
  found outside expected 404s).

### Problems

- **Days 9-21 of 30 Days of Python remain unimported** — 13 more days,
  likely 200+ more exercises given the real per-day sizes seen so far.
  Explicit backlog, not started this pass.
- **Days 22-29 are locked with zero exercises represented per-day** (no
  PDF/spec exists to name individual exercises within e.g. "Web
  scraping," only the day-level topic) — coarser than the Piscine's
  locked entries, which do have real per-exercise names. Could be
  refined later if useful.
- **French content still not started** (infrastructure only, unchanged
  from the original Sprint 3 pass) — now an even bigger backlog given
  the catalog nearly doubled again this correction.
- **The 10 locked Piscine exercises' declared `resources` paths don't
  exist as real files** (no NumPy/Pandas execution environment to run
  them against yet) — documented in `resources/README.md`, deliberately
  not fabricated.
- **`ThirtyDaysPage`'s day-jump strip and per-day accordions haven't
  been visually verified in a real browser** (no Claude-in-Chrome
  connected this session) — confirmed via `curl`/tsc/backend logs that
  the route serves 200 and the data shape is correct, but actual
  rendering (accordion open/close, sticky nav, locked-day styling) is
  unverified beyond code review.

### Next sprint

Unchanged from the original proposal, with two additions from this
correction: continue the 30-Days import (Days 9-21) as its own
multi-pass effort, and consider whether the Piscine's Module 1/2 locked
exercises should get a first real implementation once a NumPy/Pandas-
capable execution environment is designed (a bigger architectural
decision than this correction's scope). Sprint 4 not started.
