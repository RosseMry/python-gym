import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useLocale } from "../i18n/LocaleContext";
import "./ExercisePage.css";

/** Entry screen for the Timed Exam - one button, starts a fresh session. */
export function ExamStartPage() {
  const navigate = useNavigate();
  const { t } = useLocale();
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleStart() {
    setStarting(true);
    setError(null);
    try {
      const session = await api.startExam();
      navigate(`/exam/${session.session_id}`);
    } catch (e) {
      setError(String(e));
      setStarting(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("nav.exam")}</p>
        <h1>{t("exam.startTitle")}</h1>
        <p className="subtitle">{t("exam.startSubtitle")}</p>
      </header>

      {error && <p className="error-banner">{error}</p>}

      <section className="panel" style={{ textAlign: "center" }}>
        <ul style={{ textAlign: "left", maxWidth: 480, margin: "0 auto 20px" }}>
          <li>{t("exam.ruleTimed")}</li>
          <li>{t("exam.ruleNoHints")}</li>
          <li>{t("exam.ruleMixed")}</li>
        </ul>
        <button className="btn btn--primary" onClick={handleStart} disabled={starting}>
          {starting ? t("exercise.running") : t("exam.start")}
        </button>
      </section>
    </div>
  );
}
