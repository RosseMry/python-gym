import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseDetail, SubmissionResult } from "../types/exercise";
import { CodeEditor } from "../components/CodeEditor";
import { PrerequisiteWarningModal } from "../components/PrerequisiteWarningModal";
import { FunctionReferencePanel } from "../components/FunctionReferencePanel";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ExercisePage.css";

const HINT_STEP_KEYS = ["hint.step1", "hint.step2", "hint.step3"];

interface ExercisePageProps {
  onRepeatChanged: () => void;
}

export function ExercisePage({ onRepeatChanged }: ExercisePageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useLocale();
  const localize = useLocalized();

  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [code, setCode] = useState("");
  const [hints, setHints] = useState<
    { text: string; textFr: string | null; functionId: string | null }[]
  >([]);
  const [hintsExhausted, setHintsExhausted] = useState(false);
  const [prereqAcknowledged, setPrereqAcknowledged] = useState(false);
  const [openFunctionRef, setOpenFunctionRef] = useState<string | null>(null);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [solution, setSolution] = useState<{
    solution: string;
    explanation: string;
    explanationFr: string | null;
  } | null>(null);
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
    setPrereqAcknowledged(false);
    setOpenFunctionRef(null);
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
    const { hint, hint_fr, hint_function } = await api.requestHint(id!);
    if (hint === "No more hints available for this exercise.") {
      setHintsExhausted(true);
      return;
    }
    setHints((prev) => [
      ...prev,
      { text: hint, textFr: hint_fr, functionId: hint_function },
    ]);
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
    setSolution({
      solution: data.solution,
      explanation: data.explanation,
      explanationFr: data.explanation_fr,
    });
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
  const hasIncompletePrerequisites = exercise.prerequisites.some((p) => !p.solved);
  const showPrereqWarning = hasIncompletePrerequisites && !prereqAcknowledged;

  return (
    <div className="page">
      {showPrereqWarning && (
        <PrerequisiteWarningModal
          onGoBack={() => navigate("/")}
          onContinueAnyway={() => setPrereqAcknowledged(true)}
        />
      )}

      {openFunctionRef && (
        <FunctionReferencePanel
          functionId={openFunctionRef}
          onClose={() => setOpenFunctionRef(null)}
        />
      )}

      <Link to="/" className="back-link">
        {t("exercise.backToExercises")}
      </Link>

      <header className="exercise-header">
        <p className="eyebrow">{exercise.module.replace(/_/g, " ")}</p>
        <h1>{localize(exercise.title, exercise.title_fr)}</h1>
      </header>

      {exercise.prerequisites.length > 0 && (
        <section className="panel">
          <h2>{t("exercise.prerequisites")}</h2>
          <ul className="test-list">
            {exercise.prerequisites.map((prereq) => (
              <li key={prereq.id} className={prereq.solved ? "test-list__pass" : "test-list__fail"}>
                {prereq.solved ? "✓" : "○"}{" "}
                <Link to={`/exercises/${prereq.id}`}>{prereq.title}</Link>{" "}
                (
                {prereq.solved
                  ? t("exercise.prerequisiteSolved")
                  : t("exercise.prerequisiteNotSolved")}
                )
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="panel">
        <p className="exercise-description">
          {localize(exercise.description, exercise.description_fr)}
        </p>
        {exercise.examples && (
          <pre className="examples-block">
            {localize(exercise.examples, exercise.examples_fr)}
          </pre>
        )}
      </section>

      <section className="panel">
        <CodeEditor value={code} onChange={setCode} disabled={submitting} />
        <div className="actions">
          <button className="btn btn--primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? t("exercise.running") : isScript ? t("exercise.run") : t("exercise.runTests")}
          </button>
          <button className="btn" onClick={handleRequestHint} disabled={hintsExhausted}>
            {hints.length === 0 ? t("exercise.giveHint") : t("exercise.nextHint")}
          </button>
        </div>
      </section>

      {result && <ExecutionPanel result={result} />}

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
                {hint.functionId && (
                  <button
                    className="hints-panel__learn-link"
                    onClick={() => setOpenFunctionRef(hint.functionId)}
                  >
                    {t("hint.learnMore")} {hint.functionId}()
                  </button>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}

      {result?.passed && !repeatMarked && (
        <section className="panel continue-panel">
          <p className="continue-panel__prompt">{t("exercise.allTestsPassed")}</p>
          <div className="actions">
            <button className="btn btn--primary" onClick={handleContinue}>
              {t("exercise.continue")}
            </button>
            <button className="btn" onClick={handleMarkRepeat}>
              {t("exercise.repeatLater")}
            </button>
          </div>
        </section>
      )}

      {repeatMarked && (
        <section className="panel continue-panel">
          <p className="continue-panel__saved">{t("exercise.repeatQueued")}</p>
          <button className="btn btn--primary" onClick={handleContinue}>
            {t("exercise.continue")}
          </button>
        </section>
      )}

      {result?.passed && !solution && (
        <section className="panel explanation-panel">
          <h2>{t("exercise.explainTitle")}</h2>
          <p className="explanation-panel__prompt">{t("exercise.explainPrompt")}</p>
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
              {t("exercise.saveExplanation")}
            </button>
          ) : (
            <p className="explanation-panel__saved">{t("exercise.explanationSaved")}</p>
          )}
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
            <p className="solution-explanation">
              {localize(solution.explanation, solution.explanationFr)}
            </p>
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
