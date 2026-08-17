import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseDetail, SubmissionResult } from "../types/exercise";
import { CodeEditor } from "../components/CodeEditor";
import "./ExercisePage.css";

export function ExercisePage() {
  const { id } = useParams<{ id: string }>();
  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [code, setCode] = useState("");
  const [hints, setHints] = useState<string[]>([]);
  const [hintsExhausted, setHintsExhausted] = useState(false);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [solution, setSolution] = useState<{ solution: string; explanation: string } | null>(null);
  const [explanation, setExplanation] = useState("");
  const [explanationSaved, setExplanationSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setExercise(null);
    setCode("");
    setHints([]);
    setHintsExhausted(false);
    setResult(null);
    setSolution(null);
    setExplanation("");
    setExplanationSaved(false);
    api
      .getExercise(id)
      .then((data) => {
        setExercise(data);
        setCode(data.starter_code);
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
    return <div className="page">Loading exercise…</div>;
  }

  async function handleRequestHint() {
    const { hint } = await api.requestHint(id!);
    if (hint === "No more hints available for this exercise.") {
      setHintsExhausted(true);
      return;
    }
    setHints((prev) => [...prev, hint]);
  }

  async function handleSubmit() {
    setSubmitting(true);
    setResult(null);
    try {
      const outcome = await api.submit(id!, code);
      setResult(outcome);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRevealSolution() {
    const data = await api.revealSolution(id!);
    setSolution(data);
  }

  async function handleSaveExplanation() {
    await api.saveExplanation(id!, explanation);
    setExplanationSaved(true);
  }

  return (
    <div className="page">
      <Link to="/" className="back-link">
        ← Back to today's session
      </Link>

      <header className="exercise-header">
        <p className="eyebrow">{exercise.module.replace("_", " ")}</p>
        <h1>{exercise.title}</h1>
      </header>

      <section className="panel">
        <p className="exercise-description">{exercise.description}</p>
        {exercise.examples && (
          <pre className="examples-block">{exercise.examples}</pre>
        )}
      </section>

      <section className="panel">
        <CodeEditor value={code} onChange={setCode} disabled={submitting} />
        <div className="actions">
          <button className="btn btn--primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? "Running…" : "Run tests"}
          </button>
          <button className="btn" onClick={handleRequestHint} disabled={hintsExhausted}>
            {hints.length === 0 ? "I'm stuck — give me a hint" : "Next hint"}
          </button>
        </div>
      </section>

      {result && (
        <section className={`panel result-panel ${result.passed ? "result-panel--pass" : "result-panel--fail"}`}>
          <p className="result-panel__headline">
            {result.passed
              ? `All tests passed (${result.tests_passed}/${result.tests_total})`
              : `${result.tests_passed}/${result.tests_total} tests passed`}
          </p>
          {result.error && <p className="result-panel__error">{result.error}</p>}
          {result.stderr && <pre className="result-panel__stderr">{result.stderr}</pre>}
        </section>
      )}

      {hints.length > 0 && (
        <section className="panel hints-panel">
          <h2>Hints</h2>
          <ol>
            {hints.map((hint, i) => (
              <li key={i}>{hint}</li>
            ))}
          </ol>
        </section>
      )}

      {result?.passed && !solution && (
        <section className="panel explanation-panel">
          <h2>Explain your code</h2>
          <p className="explanation-panel__prompt">
            In your own words, what does your code do and why does it work?
          </p>
          <textarea
            className="explanation-textarea"
            value={explanation}
            onChange={(e) => setExplanation(e.target.value)}
            placeholder="I use total to accumulate the numbers while the for loop visits every item…"
            disabled={explanationSaved}
          />
          {!explanationSaved ? (
            <button
              className="btn"
              onClick={handleSaveExplanation}
              disabled={explanation.trim().length === 0}
            >
              Save explanation
            </button>
          ) : (
            <p className="explanation-panel__saved">Saved. Nice work.</p>
          )}
        </section>
      )}

      <section className="panel solution-panel">
        {!solution ? (
          <details>
            <summary>Reveal the solution</summary>
            <p className="solution-panel__warning">
              Only do this after real attempts and both hints — solving with
              the answer visible won't count toward mastery.
            </p>
            <button className="btn btn--muted" onClick={handleRevealSolution}>
              Show solution and explanation
            </button>
          </details>
        ) : (
          <>
            <h2>Solution</h2>
            <pre className="solution-block">{solution.solution}</pre>
            <p className="solution-explanation">{solution.explanation}</p>
          </>
        )}
      </section>
    </div>
  );
}
