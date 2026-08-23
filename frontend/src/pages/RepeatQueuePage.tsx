import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseSummary } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";

/** Lists exercises the student marked to repeat later (spec section 5). */
export function RepeatQueuePage() {
  const [exercises, setExercises] = useState<ExerciseSummary[] | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    api.getRepeatQueue().then(setExercises);
  }, []);

  if (!exercises) {
    return <div className="page">{t("repeat.loading")}</div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("repeat.eyebrow")}</p>
        <h1>{t("repeat.title")}</h1>
        <p className="subtitle">{t("repeat.subtitle")}</p>
      </header>

      {exercises.length === 0 ? (
        <p className="subtitle">{t("repeat.empty")}</p>
      ) : (
        <ul className="exercise-list">
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <Link to={`/exercises/${exercise.id}`} className="exercise-card">
                <span className="status-dot status-dot--solved_to_repeat" />
                <span className="exercise-card__title">
                  {localize(exercise.title, exercise.title_fr)}
                </span>
                <span className="exercise-card__meta">🔁 {exercise.module}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
