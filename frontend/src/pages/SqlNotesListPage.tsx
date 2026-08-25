import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { SqlLearningNoteSummary } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";
import "./LearningNote.css";

const MODULE_ICONS: Record<string, string> = {
  foundations: "🗄️",
  relational: "🔗",
  joins: "🧩",
  intermediate: "🧠",
  window: "🪟",
  dbops: "🛠️",
  views: "🔭",
  transactions: "🔁",
  indexes: "⚡",
  functions: "ƒ",
  procedures: "📋",
  triggers: "🎯",
};

/** Index of all SQL learning notes, as a card grid (mirrors LearningNotesListPage). */
export function SqlNotesListPage() {
  const [notes, setNotes] = useState<SqlLearningNoteSummary[] | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    api.listSqlNotes().then(setNotes);
  }, []);

  if (!notes) {
    return <div className="page">{t("notes.loading")}</div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("notes.eyebrow")}</p>
        <h1>{t("sql.notesTitle")}</h1>
        <p className="subtitle">{t("sql.notesSubtitle")}</p>
      </header>

      <div className="learning-note-grid">
        {notes.map((note) => (
          <Link key={note.id} to={`/sql/notes/${note.id}`} className="learning-note-grid__card">
            <span className="learning-note-grid__icon" aria-hidden="true">
              {MODULE_ICONS[note.module] ?? "📘"}
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
