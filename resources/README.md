# resources/

Supporting material that exercises can reference by path, kept separate
from exercise metadata itself (Sprint 2 spec sections 27-28).

```
resources/
├── python/
│   ├── 30-days/     Reference material for 30 Days of Python exercises
│   ├── 42-piscine/  Reference material for 42 Piscine exercises
│   └── leetcode/    Reserved for future LeetCode Top Interview 150 content
└── datasets/         Reserved for CSV/image datasets (gapminder, sample images, ...)
```

An exercise declares which resources it needs via its `resources` field,
e.g.:

```json
{
  "resources": ["python/30-days/03_day_operators.md"]
}
```

## Current status

| Resource | Source | Purpose | Used by | Required? |
|---|---|---|---|---|
| `python/30-days/03_day_operators.md` | [Asabeneh/30-Days-Of-Python](https://github.com/Asabeneh/30-Days-Of-Python), Day 3 | Reference notes for the two 30-Days exercises seeded this sprint | `30days-triangle-area`, `30days-weekly-earning` | Reference only - not required to solve the exercise |

## Locked exercises (Sprint 3 correction)

The 42 Piscine's Module 1 (Array) and Module 2 (DataTable) need
`numpy`/PIL and `pandas`/Matplotlib respectively, none of which are
part of Python-Gym's execution sandbox. Reconciled against the real
Piscine subject list (github.com/zstenger93/python_piscine) in the
Sprint 3 correction, these 10 real exercises are now seeded with
`exercise_status = "locked"` - visible in the catalog with their real
titles, but `hidden_tests`/`solution` are empty since they genuinely
can't be graded yet. Each declares its real `resources` dependency so
the path is already correct once a NumPy/Pandas track exists to
actually run them:

- **Module 1 - Array** (6 exercises): needs `numpy`/PIL and sample
  images (`landscape.jpg`/`.png`, `animal.jpeg`, `landscape.jpeg`).
- **Module 2 - DataTable** (4 exercises): needs `pandas`/Matplotlib and
  Gapminder CSV datasets (`life_expectancy_years.csv`,
  `population_total.csv`,
  `income_per_person_gdppercapita_ppp_inflation_adjusted.csv`, all
  CC-BY from gapminder.org per the subject's own instructions).

The actual image/CSV files still don't exist under `resources/` yet -
only the declared paths do, since nothing can execute against them
until a NumPy/Pandas-capable execution environment exists. When that
track is built, add the real files here and flip `exercise_status` to
`"active"`.

## Excluded exercises

Sprint 2 spec section 33 asks for a documented mechanism to exclude an
exercise from the learning path entirely (`exercise_status = "excluded"`)
- for example, a compression exercise elsewhere in the 42 Piscine that
should never show up as required. No such exercise appears in the PDFs
provided for this sprint, so nothing has actually been excluded yet;
the mechanism itself is implemented and covered by
`backend/tests/test_exercise_metadata.py`, ready for when a real
excluded exercise needs it.
