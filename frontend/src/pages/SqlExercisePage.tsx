import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { SqlExerciseDetail, SqlSubmissionResult } from "../types/exercise";
import { CodeEditor } from "../components/CodeEditor";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExercisePage.css";

const HINT_STEP_KEYS = ["hint.step1", "hint.step2", "hint.step3"];

/** SQL exercise detail: query editor, submit, results table, hints, solution. */
export function SqlExercisePage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useLocale();
  const localize = useLocalized();

  const [exercise, setExercise] = useState<SqlExerciseDetail | null>(null);
  const [query, setQuery] = useState("");
  const [hints, setHints] = useState<{ text: string; textFr: string | null }[]>([]);
  const [hintsExhausted, setHintsExhausted] = useState(false);
  const [result, setResult] = useState<SqlSubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [solution, setSolution] = useState<{ solution: string; explanation: string } | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setExercise(null);
    setQuery("");
    setHints([]);
    setHintsExhausted(false);
    setResult(null);
    setSolution(null);
    api
      .getSqlExercise(id)
      .then((data) => {
        setExercise(data);
        setQuery(data.starter_query);
      })
      .catch((e) => setError(String(e)));
  }, [id]);

  if (error) {
    return (
      <div className="page">
        <p className="error-banner">{error}</p>
      </div>
    );
  }

  if (!exercise || !id) {
    return <div className="page">{t("list.loading")}</div>;
  }

  async function handleRequestHint() {
    const { hint, hint_fr } = await api.requestSqlHint(id!);
    if (hint === "No more hints available for this exercise.") {
      setHintsExhausted(true);
      return;
    }
    setHints((prev) => [...prev, { text: hint, textFr: hint_fr }]);
  }

  async function handleSubmit() {
    setSubmitting(true);
    setResult(null);
    try {
      const outcome = await api.submitSql(id!, query);
      setResult(outcome);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRevealSolution() {
    const data = await api.revealSqlSolution(id!);
    setSolution(data);
  }

  return (
    <div className="page">
      <Link to="/sql" className="back-link">
        {t("sql.backToExercises")}
      </Link>

      <header className="exercise-header">
        <p className="eyebrow">{exercise.module.replace(/_/g, " ")}</p>
        <h1>{localize(exercise.title, exercise.title_fr)}</h1>
      </header>

      <section className="panel">
        <p className="exercise-description">
          {localize(exercise.description, exercise.description_fr)}
        </p>
        {exercise.postgres_note && (
          <p className="exercise-description">
            <strong>{t("sql.postgresNote")}:</strong> {exercise.postgres_note}
          </p>
        )}
      </section>

      <section className="panel">
        <CodeEditor
          value={query}
          onChange={setQuery}
          disabled={submitting}
          ariaLabel="SQL query editor"
        />
        <div className="actions">
          <button className="btn btn--primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? t("exercise.running") : t("sql.runQuery")}
          </button>
          <button className="btn" onClick={handleRequestHint} disabled={hintsExhausted}>
            {hints.length === 0 ? t("exercise.giveHint") : t("exercise.nextHint")}
          </button>
        </div>
      </section>

      {result && <SqlResultPanel result={result} />}

      {hints.length > 0 && (
        <section className="panel hints-panel">
          <h2>{t("exercise.hints")}</h2>
          <ol>
            {hints.map((hint, i) => (
              <li key={i}>
                <p className="hints-panel__step">
                  {t(HINT_STEP_KEYS[Math.min(i, HINT_STEP_KEYS.length - 1)])}
                </p>
                <p className="hints-panel__text">{localize(hint.text, hint.textFr)}</p>
              </li>
            ))}
          </ol>
        </section>
      )}

      <section className="panel solution-panel">
        {!solution ? (
          <details>
            <summary>{t("exercise.revealSolution")}</summary>
            <p className="solution-panel__warning">{t("exercise.revealWarning")}</p>
            <button className="btn btn--muted" onClick={handleRevealSolution}>
              {t("exercise.showSolution")}
            </button>
          </details>
        ) : (
          <>
            <h2>{t("exercise.solution")}</h2>
            <pre className="solution-block">{solution.solution}</pre>
            <p className="solution-explanation">{solution.explanation}</p>
          </>
        )}
      </section>
    </div>
  );
}

function SqlResultPanel({ result }: { result: SqlSubmissionResult }) {
  const { t } = useLocale();
  return (
    <section
      className={`panel result-panel result-panel--${
        result.status === "passed" ? "pass" : result.status === "error" ? "error" : "fail"
      }`}
    >
      <p className="result-panel__headline">
        {result.status === "passed"
          ? `All tests passed (${result.tests_passed}/${result.tests_total})`
          : result.status === "error"
            ? t("sql.executionError")
            : `${result.tests_passed}/${result.tests_total} tests passed`}
        <span className="result-panel__time">{result.execution_time.toFixed(2)}s</span>
      </p>

      {result.result_columns.length > 0 && (
        <div className="result-block">
          <p className="result-block__label">{t("sql.queryResult")}</p>
          <div className="sql-result-table-wrap">
            <table className="sql-result-table">
              <thead>
                <tr>
                  {result.result_columns.map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.result_rows.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j}>{cell === "" ? "NULL" : cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {result.tests.length > 0 && (
        <div className="result-block">
          <p className="result-block__label">Tests</p>
          <ul className="test-list">
            {result.tests.map((t, i) => (
              <li key={i} className={t.passed ? "test-list__pass" : "test-list__fail"}>
                {t.passed ? "✓" : "✗"} {t.label}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.error && (
        <div className="result-block">
          <p className="result-block__label">Error</p>
          <pre className="result-block__content result-block__content--error">
            {result.error}
          </pre>
        </div>
      )}
    </section>
  );
}
