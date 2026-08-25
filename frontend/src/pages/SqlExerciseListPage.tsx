import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../services/api";
import type { ProgressItem, SqlExerciseSummary } from "../types/exercise";
import { SQL_MODULES } from "../types/exercise";
import { TrainingBar } from "../components/TrainingBar";
import { useLocale } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";

const DIFFICULTY_LABELS = [
  "",
  "Recognition",
  "Reproduction",
  "Applied",
  "Combined",
  "Problem solving",
];

/** Index of all SQL exercises, grouped by the 12 topic-area modules. */
export function SqlExerciseListPage() {
  const [searchParams] = useSearchParams();
  const activeModule = searchParams.get("module") ?? undefined;

  const [exercises, setExercises] = useState<SqlExerciseSummary[] | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressItem>>({});
  const [error, setError] = useState<string | null>(null);
  const { t } = useLocale();

  useEffect(() => {
    setExercises(null);
    Promise.all([api.listSqlExercises(activeModule), api.listSqlProgress()])
      .then(([exerciseList, progressList]) => {
        setExercises(exerciseList);
        setProgress(Object.fromEntries(progressList.map((p) => [p.exercise_id, p])));
      })
      .catch((e) => setError(String(e)));
  }, [activeModule]);

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
  const moduleLabel =
    SQL_MODULES.find((m) => m.id === activeModule)?.label ?? t("nav.sql");

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("nav.sql")}</p>
        <h1>{moduleLabel}</h1>
        <p className="subtitle">{t("sql.listSubtitle")}</p>
      </header>

      {(activeModule ? SQL_MODULES.filter((m) => m.id === activeModule) : SQL_MODULES)
        .filter((m) => byModule[m.id]?.length)
        .map((mod) => (
          <section key={mod.id} className="module-section">
            <div className="module-section__bar">
              <TrainingBar
                label={mod.label}
                reps={byModule[mod.id].map((e) => ({
                  id: e.id,
                  status: progress[e.id]?.status ?? "NEW",
                }))}
              />
            </div>
            <ul className="exercise-list">
              {byModule[mod.id].map((exercise) => {
                const status = progress[exercise.id]?.status ?? "NEW";
                return (
                  <li key={exercise.id}>
                    <Link to={`/sql/exercises/${exercise.id}`} className="exercise-card">
                      <span className={`status-dot status-dot--${status.toLowerCase()}`} />
                      <span className="exercise-card__title">{exercise.title}</span>
                      <span className="exercise-card__meta">
                        {DIFFICULTY_LABELS[exercise.difficulty] ??
                          `Level ${exercise.difficulty}`}
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

function groupByModule(
  exercises: SqlExerciseSummary[],
): Record<string, SqlExerciseSummary[]> {
  const grouped: Record<string, SqlExerciseSummary[]> = {};
  for (const exercise of exercises) {
    (grouped[exercise.module] ??= []).push(exercise);
  }
  return grouped;
}
