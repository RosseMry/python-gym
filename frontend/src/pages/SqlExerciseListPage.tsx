import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../services/api";
import type { ProgressItem, SqlExerciseSummary } from "../types/exercise";
import { MINI_PROJECT_LABELS, SQL_MODULES } from "../types/exercise";
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

/**
 * SQL exercise index - two modes, both fetched from the same endpoint:
 * plain Foundations view (grouped by the 12 topic-area modules, none
 * of which are separate sidebar entries - see SQL_MODULES) with no
 * query param, or a Mini Project's exercises (`?project=...`, grouped
 * by `part` instead) when reached from the Mini Projects page.
 */
export function SqlExerciseListPage() {
  const [searchParams] = useSearchParams();
  const activeModule = searchParams.get("module") ?? undefined;
  const activeProject = searchParams.get("project") ?? undefined;

  const [exercises, setExercises] = useState<SqlExerciseSummary[] | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressItem>>({});
  const [error, setError] = useState<string | null>(null);
  const { t } = useLocale();

  useEffect(() => {
    setExercises(null);
    Promise.all([
      api.listSqlExercises({ module: activeModule, project: activeProject }),
      api.listSqlProgress(),
    ])
      .then(([exerciseList, progressList]) => {
        setExercises(exerciseList);
        setProgress(Object.fromEntries(progressList.map((p) => [p.exercise_id, p])));
      })
      .catch((e) => setError(String(e)));
  }, [activeModule, activeProject]);

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

  if (activeProject) {
    return (
      <MiniProjectExerciseList
        project={activeProject}
        exercises={exercises}
        progress={progress}
      />
    );
  }

  const byModule = groupByModule(exercises);
  const moduleLabel =
    SQL_MODULES.find((m) => m.id === activeModule)?.label ?? t("nav.sqlFoundations");

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
            <ExerciseCards exercises={byModule[mod.id]} progress={progress} />
          </section>
        ))}
    </div>
  );
}

function MiniProjectExerciseList({
  project,
  exercises,
  progress,
}: {
  project: string;
  exercises: SqlExerciseSummary[];
  progress: Record<string, ProgressItem>;
}) {
  const { t } = useLocale();
  const byPart = groupByPart(exercises);
  const parts = Object.keys(byPart)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div className="page">
      <Link to="/sql/mini-projects" className="back-link">
        {t("sql.backToMiniProjects")}
      </Link>
      <header className="page-header">
        <p className="eyebrow">{t("nav.miniProjects")}</p>
        <h1>{MINI_PROJECT_LABELS[project] ?? project}</h1>
        <p className="subtitle">{t("sql.miniProjectSubtitle")}</p>
      </header>

      {parts.map((part) => (
        <section key={part} className="module-section">
          <div className="module-section__bar">
            <TrainingBar
              label={`${t("sql.part")} ${part}`}
              reps={byPart[part].map((e) => ({
                id: e.id,
                status: progress[e.id]?.status ?? "NEW",
              }))}
            />
          </div>
          <ExerciseCards exercises={byPart[part]} progress={progress} />
        </section>
      ))}
    </div>
  );
}

function ExerciseCards({
  exercises,
  progress,
}: {
  exercises: SqlExerciseSummary[];
  progress: Record<string, ProgressItem>;
}) {
  return (
    <ul className="exercise-list">
      {exercises.map((exercise) => {
        const status = progress[exercise.id]?.status ?? "NEW";
        return (
          <li key={exercise.id}>
            <Link to={`/sql/exercises/${exercise.id}`} className="exercise-card">
              <span className={`status-dot status-dot--${status.toLowerCase()}`} />
              <span className="exercise-card__title">{exercise.title}</span>
              <span className="exercise-card__meta">
                {DIFFICULTY_LABELS[exercise.difficulty] ?? `Level ${exercise.difficulty}`}
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
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

function groupByPart(exercises: SqlExerciseSummary[]): Record<number, SqlExerciseSummary[]> {
  const grouped: Record<number, SqlExerciseSummary[]> = {};
  for (const exercise of exercises) {
    const part = exercise.part ?? 0;
    (grouped[part] ??= []).push(exercise);
  }
  return grouped;
}
