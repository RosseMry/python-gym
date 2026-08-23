import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseSummary } from "../types/exercise";
import "./ExerciseListPage.css";

/** Lists exercises the student marked to repeat later (spec section 5). */
export function RepeatQueuePage() {
  const [exercises, setExercises] = useState<ExerciseSummary[] | null>(null);

  useEffect(() => {
    api.getRepeatQueue().then(setExercises);
  }, []);

  if (!exercises) {
    return <div className="page">Loading your repeat queue…</div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Practice debt</p>
        <h1>Repeat queue</h1>
        <p className="subtitle">
          You solved these, but asked to see them again. They won't count
          toward mastery until you solve them cleanly, without a repeat
          flag.
        </p>
      </header>

      {exercises.length === 0 ? (
        <p className="subtitle">Nothing queued right now - nice work.</p>
      ) : (
        <ul className="exercise-list">
          {exercises.map((exercise) => (
            <li key={exercise.id}>
              <Link to={`/exercises/${exercise.id}`} className="exercise-card">
                <span className="status-dot status-dot--solved_to_repeat" />
                <span className="exercise-card__title">{exercise.title}</span>
                <span className="exercise-card__meta">🔁 {exercise.module}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
