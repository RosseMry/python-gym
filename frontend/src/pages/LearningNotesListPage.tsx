import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { LearningNoteSummary } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";
import "./LearningNote.css";

const TOPIC_ICONS: Record<string, string> = {
  lists: "🧺",
  dictionaries: "🗂️",
  strings: "🔤",
  for_loops: "🔁",
};

/** Index of all Learning Notes, as a card grid. */
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

      <div className="learning-note-grid">
        {notes.map((note) => (
          <Link key={note.id} to={`/notes/${note.id}`} className="learning-note-grid__card">
            <span className="learning-note-grid__icon" aria-hidden="true">
              {TOPIC_ICONS[note.module] ?? "📘"}
            </span>
            <span className="learning-note-grid__title">
              {localize(note.title, note.title_fr)}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
