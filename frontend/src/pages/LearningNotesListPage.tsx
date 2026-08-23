import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { LearningNoteSummary } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";

/** Index of all Learning Notes (Sprint 3), grouped as a flat list. */
export function LearningNotesListPage() {
  const [notes, setNotes] = useState<LearningNoteSummary[] | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    api.listNotes().then(setNotes);
  }, []);

  if (!notes) {
    return <div className="page">{t("notes.loading")}</div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("notes.eyebrow")}</p>
        <h1>{t("notes.title")}</h1>
        <p className="subtitle">{t("notes.subtitle")}</p>
      </header>

      <ul className="exercise-list">
        {notes.map((note) => (
          <li key={note.id}>
            <Link to={`/notes/${note.id}`} className="exercise-card">
              <span className="exercise-card__title">
                {localize(note.title, note.title_fr)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
