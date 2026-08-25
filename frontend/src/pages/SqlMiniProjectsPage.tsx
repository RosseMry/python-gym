import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { MINI_PROJECT_LABELS } from "../types/exercise";
import { useLocale } from "../i18n/LocaleContext";
import "./ExerciseListPage.css";
import "./LearningNote.css";

/**
 * Index of Mini Projects - a card per project id returned by
 * GET /api/sql/exercises/projects/list (currently just
 * ecommerce_sales_analysis, the pilot). Adding a new Mini Project
 * later needs no change here: it appears automatically once its
 * exercises are seeded, labeled via MINI_PROJECT_LABELS.
 */
export function SqlMiniProjectsPage() {
  const [projects, setProjects] = useState<string[] | null>(null);
  const { t } = useLocale();

  useEffect(() => {
    api.listSqlMiniProjects().then(setProjects);
  }, []);

  if (!projects) {
    return <div className="page">{t("list.loading")}</div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="eyebrow">{t("nav.sql")}</p>
        <h1>{t("nav.miniProjects")}</h1>
        <p className="subtitle">{t("sql.miniProjectsSubtitle")}</p>
      </header>

      {projects.length === 0 ? (
        <p className="subtitle">{t("sql.noMiniProjectsYet")}</p>
      ) : (
        <div className="learning-note-grid">
          {projects.map((project) => (
            <Link
              key={project}
              to={`/sql?project=${project}`}
              className="learning-note-grid__card"
            >
              <span className="learning-note-grid__icon" aria-hidden="true">
                📦
              </span>
              <span className="learning-note-grid__title">
                {MINI_PROJECT_LABELS[project] ?? project}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
