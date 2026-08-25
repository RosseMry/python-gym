import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { SqlLearningNoteDetail, SqlLearningNoteSummary } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import { SqlCode } from "../components/SqlCode";
import "./ExercisePage.css";
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

function splitNumberedItems(text: string): string[] {
  return text
    .split(/\n\s*\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

/** One SQL Learning Notes theory page (mirrors LearningNotePage's design). */
export function SqlNotePage() {
  const { id } = useParams<{ id: string }>();
  const [note, setNote] = useState<SqlLearningNoteDetail | null>(null);
  const [allNotes, setAllNotes] = useState<SqlLearningNoteSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    if (!id) return;
    setNote(null);
    api.getSqlNote(id).then(setNote).catch((e) => setError(String(e)));
    api.listSqlNotes().then(setAllNotes);
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

  const currentIndex = allNotes.findIndex((n) => n.id === id);
  const previousNote = currentIndex > 0 ? allNotes[currentIndex - 1] : null;
  const nextNote =
    currentIndex >= 0 && currentIndex < allNotes.length - 1
      ? allNotes[currentIndex + 1]
      : null;

  const mistakes = splitNumberedItems(localize(note.common_mistakes, note.common_mistakes_fr));

  return (
    <div className="page learning-note">
      <Link to="/sql/notes" className="back-link">
        {t("sql.backToNotes")}
      </Link>

      <header className="learning-note__hero">
        <span className="learning-note__hero-icon" aria-hidden="true">
          {MODULE_ICONS[note.module] ?? "📘"}
        </span>
        <div>
          <p className="eyebrow">{t("notes.eyebrow")}</p>
          <h1>{localize(note.title, note.title_fr)}</h1>
        </div>
      </header>

      <section className="learning-note__card learning-note__card--key-idea">
        <span className="learning-note__card-icon" aria-hidden="true">💡</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("sql.whatIsIt")}</p>
          <p className="learning-note__key-idea-text">
            {localize(note.what_is_it, note.what_is_it_fr)}
          </p>
        </div>
      </section>

      <section className="learning-note__card">
        <span className="learning-note__card-icon" aria-hidden="true">🎯</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("sql.whyItMatters")}</p>
          <p className="learning-note__card-text">
            {localize(note.why_it_matters, note.why_it_matters_fr)}
          </p>
        </div>
      </section>

      <section className="learning-note__code-panel">
        <div className="learning-note__code-header">
          <span className="learning-note__code-dot learning-note__code-dot--red" />
          <span className="learning-note__code-dot learning-note__code-dot--yellow" />
          <span className="learning-note__code-dot learning-note__code-dot--green" />
          <span className="learning-note__code-title">{t("notes.syntax")}</span>
        </div>
        <pre className="learning-note__code-block">
          <SqlCode code={localize(note.syntax, note.syntax_fr)} />
        </pre>
      </section>

      <section className="learning-note__code-panel">
        <div className="learning-note__code-header">
          <span className="learning-note__code-dot learning-note__code-dot--red" />
          <span className="learning-note__code-dot learning-note__code-dot--yellow" />
          <span className="learning-note__code-dot learning-note__code-dot--green" />
          <span className="learning-note__code-title">{t("notes.examples")}</span>
        </div>
        <pre className="learning-note__code-block">
          <SqlCode code={note.example} />
        </pre>
      </section>

      <section className="panel">
        <h2>{t("sql.output")}</h2>
        <pre className="examples-block">{note.output}</pre>
      </section>

      {note.postgres_note && (
        <section className="learning-note__card">
          <span className="learning-note__card-icon" aria-hidden="true">🐘</span>
          <div className="learning-note__card-body">
            <p className="learning-note__card-label">{t("sql.postgresNote")}</p>
            <p className="learning-note__card-text">{note.postgres_note}</p>
          </div>
        </section>
      )}

      <section className="learning-note__card learning-note__card--warning">
        <span className="learning-note__card-icon" aria-hidden="true">⚠️</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("notes.commonMistakes")}</p>
          <ol className="learning-note__mistake-list">
            {mistakes.map((mistake) => (
              <li key={mistake.slice(0, 24)}>{mistake}</li>
            ))}
          </ol>
        </div>
      </section>

      <section className="learning-note__card learning-note__card--try">
        <span className="learning-note__card-icon" aria-hidden="true">✏️</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("notes.miniExercise")}</p>
          <p className="learning-note__card-text">
            {localize(note.mini_exercise, note.mini_exercise_fr)}
          </p>
        </div>
      </section>

      {note.related_exercise_ids.length > 0 && (
        <section className="panel">
          <h2>{t("notes.relatedExercises")}</h2>
          <div className="learning-note__related-grid">
            {note.related_exercise_ids.map((exerciseId) => (
              <Link
                key={exerciseId}
                to={`/sql/exercises/${exerciseId}`}
                className="learning-note__related-chip"
              >
                {exerciseId}
              </Link>
            ))}
          </div>
        </section>
      )}

      {(previousNote || nextNote) && (
        <nav className="learning-note__pager">
          {previousNote ? (
            <Link
              to={`/sql/notes/${previousNote.id}`}
              className="learning-note__pager-link learning-note__pager-link--previous"
            >
              <span className="learning-note__pager-label">{t("notes.previous")}</span>
              <span className="learning-note__pager-title">
                {localize(previousNote.title, previousNote.title_fr)}
              </span>
            </Link>
          ) : (
            <span />
          )}
          {nextNote && (
            <Link
              to={`/sql/notes/${nextNote.id}`}
              className="learning-note__pager-link learning-note__pager-link--next"
            >
              <span className="learning-note__pager-label">{t("notes.next")}</span>
              <span className="learning-note__pager-title">
                {localize(nextNote.title, nextNote.title_fr)}
              </span>
            </Link>
          )}
        </nav>
      )}
    </div>
  );
}
