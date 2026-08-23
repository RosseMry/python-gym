import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseSummary, ProgressItem } from "../types/exercise";
import { CONTENT_SOURCES } from "../types/exercise";
import { TrainingBar } from "../components/TrainingBar";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";

const MODULE_LABELS: Record<string, string> = {
  conditions: "Conditions",
  for_loops: "For loops",
  lists: "Lists",
  input_and_formulas: "Input & formulas",
  piscine_00_starting: "Starting",
  piscine_01_array: "Array",
  piscine_02_datatable: "DataTable",
  piscine_03_oop: "Object-Oriented Programming",
  piscine_04_data_oriented_design: "Data Oriented Design",
  // Sprint 3 foundations/python_gym/progressive-bridge modules
  variables: "Variables",
  types: "Types",
  input_output: "Input & output",
  operators: "Operators",
  strings: "Strings",
  tuples: "Tuples",
  sets: "Sets",
  dictionaries: "Dictionaries",
  functions: "Functions",
  scope: "Scope & closures",
  exceptions: "Exceptions",
  comprehensions: "Comprehensions",
  files: "Files",
  modules: "Modules",
  oop: "Object-Oriented Programming",
  iterators_generators: "Iterators & generators",
  nested_structures: "Nested structures",
  nested_lists: "Nested lists",
};

const DIFFICULTY_LABELS = ["", "Recognition", "Reproduction", "Applied", "Combined", "Problem solving"];

export function ExerciseListPage() {
  const [searchParams] = useSearchParams();
  const source = searchParams.get("source") ?? undefined;

  const [exercises, setExercises] = useState<ExerciseSummary[] | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressItem>>({});
  const [error, setError] = useState<string | null>(null);
  const [nextId, setNextId] = useState<string | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    setExercises(null);
    setNextId(null);
    Promise.all([api.listExercises({ source }), api.listProgress()])
      .then(([exerciseList, progressList]) => {
        setExercises(exerciseList);
        setProgress(Object.fromEntries(progressList.map((p) => [p.exercise_id, p])));
      })
      .catch((e) => setError(String(e)));
    api.getNextExercise(source).then((next) => setNextId(next?.id ?? null));
  }, [source]);

  if (error) {
    return (
      <div className="page">
        <p className="error-banner">
          {t("list.backendError")}
          <br />
          <code>{error}</code>
        </p>
      </div>
    );
  }

  if (!exercises) {
    return <div className="page">{t("list.loading")}</div>;
  }

  const byModule = groupByModule(exercises);
  const sourceParts = source?.split(",") ?? [];
  const heading =
    sourceParts.length > 1
      ? t("nav.foundations")
      : source
        ? CONTENT_SOURCES[source as keyof typeof CONTENT_SOURCES] ?? source
        : t("list.todaysSession");

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("brand")}</p>
        <h1>{heading}</h1>
        <p className="subtitle">{t("list.subtitle")}</p>
        {nextId && (
          <Link to={`/exercises/${nextId}`} className="page-header__cta">
            {t("list.continueWhereYouLeftOff")}
          </Link>
        )}
      </header>

      {Object.entries(byModule).map(([module, items]) => (
        <section key={module} className="module-section">
          <div className="module-section__bar">
            <TrainingBar
              label={MODULE_LABELS[module] ?? module}
              reps={items
                .filter((e) => e.exercise_status !== "locked")
                .map((e) => ({
                  id: e.id,
                  status: progress[e.id]?.status ?? "NEW",
                }))}
            />
          </div>
          <ul className="exercise-list">
            {items.map((exercise) => {
              if (exercise.exercise_status === "locked") {
                return (
                  <li key={exercise.id}>
                    <span className="exercise-card exercise-card--locked">
                      <span className="status-dot status-dot--locked" />
                      <span className="exercise-card__title">
                        🔒 {localize(exercise.title, exercise.title_fr)}
                      </span>
                      <span className="exercise-card__meta">{t("list.locked")}</span>
                    </span>
                  </li>
                );
              }
              const status = progress[exercise.id]?.status ?? "NEW";
              return (
                <li key={exercise.id}>
                  <Link to={`/exercises/${exercise.id}`} className="exercise-card">
                    <span className={`status-dot status-dot--${status.toLowerCase()}`} />
                    <span className="exercise-card__title">
                      {localize(exercise.title, exercise.title_fr)}
                    </span>
                    <span className="exercise-card__meta">
                      {DIFFICULTY_LABELS[exercise.difficulty] ?? `Level ${exercise.difficulty}`}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </section>
      ))}
    </div>
  );
}

function groupByModule(exercises: ExerciseSummary[]): Record<string, ExerciseSummary[]> {
  const grouped: Record<string, ExerciseSummary[]> = {};
  for (const exercise of exercises) {
    (grouped[exercise.module] ??= []).push(exercise);
  }
  return grouped;
}
