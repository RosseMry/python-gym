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

## Not yet included (Sprint 2 scope note)

The 42 Piscine's "Python for Data Science" series (the same set of
PDFs used to build this sprint's `42_python_piscine` content) also
includes two data-heavy modules that are **out of scope for Sprint 2**
per the "no scope creep" rule (NumPy/Pandas are explicitly excluded
this sprint):

- **Module 1 - Array**: needs `numpy`/PIL and sample images
  (`landscape.jpg`, `animal.jpeg`).
- **Module 2 - DataTable**: needs `pandas` and Gapminder CSV datasets
  (`life_expectancy_years.csv`, `population_total.csv`,
  `income_per_person_gdppercapita_ppp_inflation_adjusted.csv`, all
  CC-BY from gapminder.org per the subject's own instructions).

Their exercise statements exist (in the PDFs) but are not seeded as
Python-Gym content yet. When a future sprint adds the NumPy/Pandas
track, `resources/datasets/` is where those CSVs and sample images
should live, declared as `resources` on the corresponding exercises.

## Excluded exercises

Sprint 2 spec section 33 asks for a documented mechanism to exclude an
exercise from the learning path entirely (`exercise_status = "excluded"`)
- for example, a compression exercise elsewhere in the 42 Piscine that
should never show up as required. No such exercise appears in the PDFs
provided for this sprint, so nothing has actually been excluded yet;
the mechanism itself is implemented and covered by
`backend/tests/test_exercise_metadata.py`, ready for when a real
excluded exercise needs it.
