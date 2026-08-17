import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseSummary, ProgressItem } from "../types/exercise";
import { TrainingBar } from "../components/TrainingBar";
import "./ExerciseListPage.css";

const MODULE_LABELS: Record<string, string> = {
  conditions: "Conditions",
  for_loops: "For loops",
  lists: "Lists",
};

const DIFFICULTY_LABELS = ["", "Recognition", "Reproduction", "Applied", "Combined", "Problem solving"];

export function ExerciseListPage() {
  const [exercises, setExercises] = useState<ExerciseSummary[] | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressItem>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listExercises(), api.listProgress()])
      .then(([exerciseList, progressList]) => {
        setExercises(exerciseList);
        setProgress(Object.fromEntries(progressList.map((p) => [p.exercise_id, p])));
      })
      .catch((e) => setError(String(e)));
  }, []);

  if (error) {
    return (
      <div className="page">
        <p className="error-banner">
          Couldn't reach the backend. Is it running on port 8000?
          <br />
          <code>{error}</code>
        </p>
      </div>
    );
  }

  if (!exercises) {
    return <div className="page">Loading today's exercises…</div>;
  }

  const byModule = groupByModule(exercises);

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">Python Gym</p>
        <h1>Today's session</h1>
        <p className="subtitle">
          Read the problem, think before you type, and only ask for a hint
          once you're actually stuck.
        </p>
      </header>

      {Object.entries(byModule).map(([module, items]) => (
        <section key={module} className="module-section">
          <div className="module-section__bar">
            <TrainingBar
              label={MODULE_LABELS[module] ?? module}
              reps={items.map((e) => ({
                id: e.id,
                status: progress[e.id]?.status ?? "NEW",
              }))}
            />
          </div>
          <ul className="exercise-list">
            {items.map((exercise) => {
              const status = progress[exercise.id]?.status ?? "NEW";
              return (
                <li key={exercise.id}>
                  <Link to={`/exercises/${exercise.id}`} className="exercise-card">
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
