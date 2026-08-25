import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../services/api";
import type { ExamResult, ExamSessionResponse } from "../types/exercise";
import { CodeEditor } from "../components/CodeEditor";
import { useLocale } from "../i18n/LocaleContext";
import "./ExercisePage.css";
import "./ExamPage.css";

/**
 * The Timed Exam's question flow AND results screen in one page - the
 * backend only returns a result from the submit call itself (there's
 * no separate GET-results endpoint), so keeping both here avoids an
 * awkward "where do results live" routing question, the same way
 * ExercisePage shows its own submission result inline.
 */
export function ExamPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { t } = useLocale();

  const [session, setSession] = useState<ExamSessionResponse | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null);
  const [result, setResult] = useState<ExamResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submittedRef = useRef(false);

  useEffect(() => {
    if (!sessionId) return;
    api
      .getExamSession(sessionId)
      .then(setSession)
      .catch((e) => setError(String(e)));
  }, [sessionId]);

  const handleSubmit = useCallback(async () => {
    if (!sessionId || submittedRef.current) return;
    submittedRef.current = true;
    setSubmitting(true);
    try {
      const outcome = await api.submitExam(sessionId, answers);
      setResult(outcome);
    } catch (e) {
      setError(String(e));
      submittedRef.current = false;
    } finally {
      setSubmitting(false);
    }
  }, [sessionId, answers]);

  // A ref holds the latest submit closure so the timer effect below
  // doesn't need `handleSubmit` (which changes every keystroke, since
  // it closes over `answers`) in its dependency array - that would
  // tear down and restart the interval on every keystroke otherwise.
  const handleSubmitRef = useRef(handleSubmit);
  handleSubmitRef.current = handleSubmit;

  useEffect(() => {
    if (!session || result) return;
    const deadline = new Date(session.deadline_at).getTime();
    const tick = () => {
      const secondsLeft = Math.max(0, Math.floor((deadline - Date.now()) / 1000));
      setRemainingSeconds(secondsLeft);
      if (secondsLeft <= 0) {
        handleSubmitRef.current();
      }
    };
    tick();
    const interval = window.setInterval(tick, 1000);
    return () => window.clearInterval(interval);
  }, [session, result]);

  if (error) {
    return (
      <div className="page">
        <p className="error-banner">{error}</p>
      </div>
    );
  }

  if (!session) {
    return <div className="page">{t("list.loading")}</div>;
  }

  if (result) {
    return <ExamResultsPanel result={result} />;
  }

  const minutes = remainingSeconds !== null ? Math.floor(remainingSeconds / 60) : 0;
  const seconds = remainingSeconds !== null ? remainingSeconds % 60 : 0;
  const timeLow = remainingSeconds !== null && remainingSeconds <= 60;

  return (
    <div className="page">
      <header className="exam-timer-bar">
        <p className="eyebrow">{t("nav.exam")}</p>
        <p className={`exam-timer-bar__clock ${timeLow ? "exam-timer-bar__clock--low" : ""}`}>
          {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
        </p>
      </header>

      {session.questions.map((question, index) => (
        <section key={question.id} className="panel exam-question">
          <p className="exam-question__number">
            {t("exam.question")} {index + 1} / {session.questions.length} ·{" "}
            {question.points} {question.points === 1 ? t("exam.point") : t("exam.points")}
          </p>
          <pre className="exam-question__prompt">{question.prompt}</pre>
          {question.code_snippet && (
            <pre className="examples-block">{question.code_snippet}</pre>
          )}

          {question.kind === "mcq" && question.choices && (
            <div className="exam-question__choices">
              {question.choices.map((choice, choiceIndex) => (
                <label key={choiceIndex} className="exam-question__choice">
                  <input
                    type="radio"
                    name={question.id}
                    checked={answers[question.id] === String(choiceIndex)}
                    onChange={() =>
                      setAnswers((prev) => ({ ...prev, [question.id]: String(choiceIndex) }))
                    }
                  />
                  {choice}
                </label>
              ))}
            </div>
          )}

          {(question.kind === "output_prediction" || question.kind === "debugging") && (
            <input
              className="exam-question__text-input"
              type="text"
              value={answers[question.id] ?? ""}
              onChange={(e) =>
                setAnswers((prev) => ({ ...prev, [question.id]: e.target.value }))
              }
              placeholder={t("exam.typeAnswer")}
            />
          )}

          {question.kind === "coding" && (
            <CodeEditor
              value={answers[question.id] ?? question.starter_code ?? ""}
              onChange={(value) =>
                setAnswers((prev) => ({ ...prev, [question.id]: value }))
              }
              ariaLabel={`Code editor for question ${index + 1}`}
            />
          )}
        </section>
      ))}

      <section className="panel" style={{ textAlign: "center" }}>
        <button className="btn btn--primary" onClick={handleSubmit} disabled={submitting}>
          {submitting ? t("exercise.running") : t("exam.submit")}
        </button>
      </section>
    </div>
  );
}

function ExamResultsPanel({ result }: { result: ExamResult }) {
  const { t } = useLocale();
  const percent = result.max_score > 0 ? Math.round((result.score / result.max_score) * 100) : 0;
  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("nav.exam")}</p>
        <h1>{t("exam.resultsTitle")}</h1>
      </header>

      <section className="panel exam-results__summary">
        <p className="exam-results__score">
          {result.score} / {result.max_score}
        </p>
        <p className="exam-results__percent">{percent}%</p>
        <p className="subtitle">
          {result.questions_correct} / {result.questions_total} {t("exam.correct")} ·{" "}
          {result.status === "timed_out" ? t("exam.timedOut") : t("exam.submitted")}
        </p>
      </section>

      <section className="panel">
        <h2>{t("exam.breakdown")}</h2>
        <ul className="test-list">
          {result.answers.map((answer) => (
            <li
              key={answer.question_id}
              className={answer.correct ? "test-list__pass" : "test-list__fail"}
            >
              {answer.correct ? "✓" : "✗"} {answer.question_id} — {answer.points_earned}/
              {answer.points_possible}
            </li>
          ))}
        </ul>
      </section>

      <Link to="/exam" className="back-link">
        {t("exam.takeAnother")}
      </Link>
    </div>
  );
}
