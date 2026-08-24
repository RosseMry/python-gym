import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { LearningNoteDetail, LearningNoteSummary } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import { PythonCode } from "../components/PythonCode";
import "./ExercisePage.css";
import "./LearningNote.css";

const TOPIC_ICONS: Record<string, string> = {
  lists: "🧺",
  dictionaries: "🗂️",
  strings: "🔤",
  for_loops: "🔁",
};

// Common-mistake text is stored as one blob, numbered items separated
// by a blank line ("1. ...\n\n2. ..."). Splitting on that blank line
// turns it into distinct rows instead of one dense paragraph.
function splitNumberedItems(text: string): string[] {
  return text
    .split(/\n\s*\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

// The mini-exercise text ends with a parenthetical answer - "(Answer:
// ...)" in English, "(Réponse : ...)" in French - written that way so
// it can be split off and hidden behind a reveal instead of spoiling
// the prediction immediately.
function splitQuestionAndAnswer(text: string): { question: string; answer: string | null } {
  const match = text.match(/\n\s*\n(\(Answer:|\(Réponse\s*:)([\s\S]*)$/);
  if (!match) {
    return { question: text.trim(), answer: null };
  }
  const question = text.slice(0, match.index).trim();
  const answer = (match[1] + match[2]).replace(/^\(|\)$/g, "").trim();
  return { question, answer };
}

/**
 * One Learning Notes theory page: key idea, syntax, examples, a
 * common-mistake warning card, a mini exercise card with a hidden
 * answer, related practice exercises, and previous/next navigation
 * through the note set (ordered by display_order, same order the
 * index page and the API already use).
 */
export function LearningNotePage() {
  const { id } = useParams<{ id: string }>();
  const [note, setNote] = useState<LearningNoteDetail | null>(null);
  const [allNotes, setAllNotes] = useState<LearningNoteSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [answerRevealed, setAnswerRevealed] = useState(false);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    if (!id) return;
    setNote(null);
    setAnswerRevealed(false);
    api.getNote(id).then(setNote).catch((e) => setError(String(e)));
    api.listNotes().then(setAllNotes);
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
  const { question, answer } = splitQuestionAndAnswer(
    localize(note.mini_exercise, note.mini_exercise_fr),
  );

  return (
    <div className="page learning-note">
      <Link to="/notes" className="back-link">
        {t("exercise.backToExercises")}
      </Link>

      <header className="learning-note__hero">
        <span className="learning-note__hero-icon" aria-hidden="true">
          {TOPIC_ICONS[note.module] ?? "📘"}
        </span>
        <div>
          <p className="eyebrow">{t("notes.eyebrow")}</p>
          <h1>{localize(note.title, note.title_fr)}</h1>
        </div>
      </header>

      <section className="learning-note__card learning-note__card--key-idea">
        <span className="learning-note__card-icon" aria-hidden="true">💡</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("notes.keyIdea")}</p>
          <p className="learning-note__key-idea-text">
            {localize(note.explanation, note.explanation_fr)}
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
          <PythonCode code={localize(note.syntax, note.syntax_fr)} />
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
          <PythonCode code={localize(note.examples, note.examples_fr)} />
        </pre>
      </section>

      <section className="learning-note__card learning-note__card--warning">
        <span className="learning-note__card-icon" aria-hidden="true">⚠️</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("notes.commonMistakes")}</p>
          <ol className="learning-note__mistake-list">
            {mistakes.map((mistake) => (
              <li key={mistake.slice(0, 24)}>{mistake.replace(/^\d+\.\s*/, "")}</li>
            ))}
          </ol>
        </div>
      </section>

      <section className="learning-note__card learning-note__card--try">
        <span className="learning-note__card-icon" aria-hidden="true">✏️</span>
        <div className="learning-note__card-body">
          <p className="learning-note__card-label">{t("notes.miniExercise")}</p>
          <p className="learning-note__card-text">{question}</p>
          {answer && (
            <details
              className="learning-note__reveal"
              open={answerRevealed}
              onToggle={(e) => setAnswerRevealed(e.currentTarget.open)}
            >
              <summary>{answerRevealed ? t("notes.hideAnswer") : t("notes.revealAnswer")}</summary>
              <p className="learning-note__reveal-text">{answer}</p>
            </details>
          )}
        </div>
      </section>

      {note.related_exercise_ids.length > 0 && (
        <section className="panel">
          <h2>{t("notes.relatedExercises")}</h2>
          <div className="learning-note__related-grid">
            {note.related_exercise_ids.map((exerciseId) => (
              <Link
                key={exerciseId}
                to={`/exercises/${exerciseId}`}
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
              to={`/notes/${previousNote.id}`}
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
              to={`/notes/${nextNote.id}`}
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
