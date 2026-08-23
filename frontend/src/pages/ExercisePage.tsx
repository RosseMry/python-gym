import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseDetail, SubmissionResult } from "../types/exercise";
import { CodeEditor } from "../components/CodeEditor";
import "./ExercisePage.css";

interface ExercisePageProps {
  onRepeatChanged: () => void;
}

export function ExercisePage({ onRepeatChanged }: ExercisePageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [code, setCode] = useState("");
  const [hints, setHints] = useState<string[]>([]);
  const [hintsExhausted, setHintsExhausted] = useState(false);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [solution, setSolution] = useState<{ solution: string; explanation: string } | null>(null);
  const [explanation, setExplanation] = useState("");
  const [explanationSaved, setExplanationSaved] = useState(false);
  const [repeatMarked, setRepeatMarked] = useState(false);
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
    setRepeatMarked(false);
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

  async function handleMarkRepeat() {
    await api.markRepeat(id!);
    setRepeatMarked(true);
    onRepeatChanged();
  }

  function handleContinue() {
    navigate("/");
  }

  const isScript = exercise.exercise_type === "script";

  return (
    <div className="page">
      <Link to="/" className="back-link">
        ← Back to exercises
      </Link>

      <header className="exercise-header">
        <p className="eyebrow">{exercise.module.replace(/_/g, " ")}</p>
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
            {submitting ? "Running…" : isScript ? "Run" : "Run tests"}
          </button>
          <button className="btn" onClick={handleRequestHint} disabled={hintsExhausted}>
            {hints.length === 0 ? "I'm stuck — give me a hint" : "Next hint"}
          </button>
        </div>
      </section>

      {result && <ExecutionPanel result={result} />}

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

      {result?.passed && !repeatMarked && (
        <section className="panel continue-panel">
          <p className="continue-panel__prompt">
            All tests passed. Ready to move on, or want to see this one
            again later?
          </p>
          <div className="actions">
            <button className="btn btn--primary" onClick={handleContinue}>
              Continue
            </button>
            <button className="btn" onClick={handleMarkRepeat}>
              🔁 Repeat later
            </button>
          </div>
        </section>
      )}

      {repeatMarked && (
        <section className="panel continue-panel">
          <p className="continue-panel__saved">
            🔁 Queued for later. Find it any time in the Repeat queue.
          </p>
          <button className="btn btn--primary" onClick={handleContinue}>
            Continue
          </button>
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

/**
 * The Sprint 2 execution feedback panel: the student's own output,
 * individual test results, errors, and (for 42-piscine exercises) a
 * separate style check - never mixed with hidden-test internals.
 */
function ExecutionPanel({ result }: { result: SubmissionResult }) {
  return (
    <section
      className={`panel result-panel result-panel--${result.status === "passed" ? "pass" : result.status === "error" ? "error" : "fail"}`}
    >
      <p className="result-panel__headline">
        {result.status === "passed" && result.tests_total > 0
          ? `All tests passed (${result.tests_passed}/${result.tests_total})`
          : result.status === "passed"
            ? "Ran successfully"
            : result.status === "error"
              ? "Execution error"
              : `${result.tests_passed}/${result.tests_total} tests passed`}
        <span className="result-panel__time">{result.execution_time.toFixed(2)}s</span>
      </p>

      {result.stdout.trim() && (
        <div className="result-block">
          <p className="result-block__label">Output</p>
          <pre className="result-block__content">{result.stdout}</pre>
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

      {result.stderr.trim() && (
        <div className="result-block">
          <p className="result-block__label">stderr</p>
          <pre className="result-block__content result-block__content--error">
            {result.stderr}
          </pre>
        </div>
      )}

      {result.style && (
        <div className="result-block">
          <p className="result-block__label">
            Style {result.style.ran ? (result.style.passed ? "✓" : "✗") : "(unavailable)"}
          </p>
          {result.style.output && (
            <pre className="result-block__content">{result.style.output}</pre>
          )}
        </div>
      )}
    </section>
  );
}
