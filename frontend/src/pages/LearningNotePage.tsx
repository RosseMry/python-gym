import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { LearningNoteDetail } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExercisePage.css";
import "./LearningNote.css";

/**
 * One Learning Notes theory page (Sprint 3, redesigned as cards in the
 * Sprint 3 correction): key idea, syntax, examples, a common-mistake
 * warning card, a mini exercise card, then links to real practice
 * exercises for the topic.
 */
export function LearningNotePage() {
  const { id } = useParams<{ id: string }>();
  const [note, setNote] = useState<LearningNoteDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    if (!id) return;
    setNote(null);
    api.getNote(id).then(setNote).catch((e) => setError(String(e)));
  }, [id]);

  if (error) {
    return (
      <div className="page">
        <p className="error-banner">{error}</p>
      </div>
    );
  }

  if (!note) {
    return <div className="page">{t("notes.loading")}</div>;
  }

  return (
    <div className="page learning-note">
      <Link to="/notes" className="back-link">
        {t("exercise.backToExercises")}
      </Link>

      <header className="exercise-header">
        <p className="eyebrow">{t("notes.eyebrow")}</p>
        <h1>{localize(note.title, note.title_fr)}</h1>
      </header>

      <section className="learning-note__card learning-note__card--key-idea">
        <p className="learning-note__card-label">{t("notes.keyIdea")}</p>
        <p className="learning-note__key-idea-text">
          {localize(note.explanation, note.explanation_fr)}
        </p>
      </section>

      <section className="panel">
        <h2>{t("notes.syntax")}</h2>
        <pre className="solution-block">{localize(note.syntax, note.syntax_fr)}</pre>
      </section>

      <section className="panel">
        <h2>{t("notes.examples")}</h2>
        <pre className="examples-block">{localize(note.examples, note.examples_fr)}</pre>
      </section>

      <section className="learning-note__card learning-note__card--warning">
        <p className="learning-note__card-label">⚠️ {t("notes.commonMistakes")}</p>
        <p className="learning-note__card-text">
          {localize(note.common_mistakes, note.common_mistakes_fr)}
        </p>
      </section>

      <section className="learning-note__card learning-note__card--try">
        <p className="learning-note__card-label">✏️ {t("notes.miniExercise")}</p>
        <p className="learning-note__card-text">
          {localize(note.mini_exercise, note.mini_exercise_fr)}
        </p>
      </section>

      {note.related_exercise_ids.length > 0 && (
        <section className="panel">
          <h2>{t("notes.relatedExercises")}</h2>
          <ul className="exercise-list">
            {note.related_exercise_ids.map((exerciseId) => (
              <li key={exerciseId}>
                <Link to={`/exercises/${exerciseId}`} className="exercise-card">
                  <span className="exercise-card__title">{exerciseId}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
