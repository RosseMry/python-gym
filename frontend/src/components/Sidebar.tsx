import { useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { useLocale } from "../i18n/LocaleContext";
import { SQL_MODULES } from "../types/exercise";
import "./Sidebar.css";

interface SidebarProps {
  repeatCount: number;
}

// Sprint 3 correction: Foundations/Progressive Python/Python-Gym are
// not separate tracks - they're one merged "Progressive -> Foundations"
// content stream (spec: "Python-Gym exercises are not a separate
// sidebar track. They are integrated into the Progressive learning
// system."), fetched as one multi-source request. 30 Days of Python
// gets its own dedicated page (day/level structure), not a source
// filter. 42 Piscine stays separate, one level down: its own section.
const FOUNDATIONS_SOURCES = "foundations,progressive_python,python_gym";

// Sprint 4: SQL is now a real, implemented track - Data Science stays
// a roadmap-only placeholder (spec: not implemented this sprint).
const COMING_SOON = ["Data Science", "Mathematics", "Machine Learning", "ML Piscine"];

/**
 * The learning-track sidebar. Foundations / 30 Days / 42 Piscine live
 * inside a single collapsible "Python" group, since they're all the
 * same language track - Notes and the Exam are Python-only content
 * right now, so they live inside that same group too (not as their
 * own top-level sections) rather than implying they cover more than
 * they do. SQL (Sprint 4) gets its own collapsible group one level
 * down, one link per topic area, plus its own Notes link - SQL's
 * theory pages are a separate content type (SqlLearningNote, with a
 * postgres_note field Python's LearningNote doesn't need). The moment
 * either Notes or the Exam grows to cover more than one language,
 * this is the place to pull it back out to a shared top-level link.
 */
export function Sidebar({ repeatCount }: SidebarProps) {
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { locale, setLocale, t } = useLocale();
  const [pythonOpen, setPythonOpen] = useState(true);
  const [sqlOpen, setSqlOpen] = useState(false);

  const isNotesActive = location.pathname.startsWith("/notes");
  const isSqlNotesActive = location.pathname.startsWith("/sql/notes");
  const isExamActive = location.pathname.startsWith("/exam");

  return (
    <nav className="sidebar">
      <div className="sidebar__top">
        <Link to="/" className="sidebar__brand">
          {t("brand")}
        </Link>
        <div className="sidebar__locale-toggle">
          <button
            className={locale === "en" ? "sidebar__locale-btn--active" : "sidebar__locale-btn"}
            onClick={() => setLocale("en")}
          >
            {t("locale.en")}
          </button>
          <button
            className={locale === "fr" ? "sidebar__locale-btn--active" : "sidebar__locale-btn"}
            onClick={() => setLocale("fr")}
          >
            {t("locale.fr")}
          </button>
        </div>
      </div>

      {repeatCount > 0 && (
        <Link
          to="/repeat"
          className={`sidebar__repeat ${location.pathname === "/repeat" ? "sidebar__repeat--active" : ""}`}
        >
          🔁 {t("nav.repeatQueue")}
          <span className="sidebar__badge">{repeatCount}</span>
        </Link>
      )}

      <div className="sidebar__section">
        <button
          type="button"
          className="sidebar__section-toggle"
          onClick={() => setPythonOpen((open) => !open)}
          aria-expanded={pythonOpen}
        >
          <span className="sidebar__section-title">{t("nav.python")}</span>
          <span className={`sidebar__chevron ${pythonOpen ? "sidebar__chevron--open" : ""}`}>
            ▸
          </span>
        </button>
        {pythonOpen && (
          <ul className="sidebar__list sidebar__list--nested">
            <li>
              <Link
                to="/notes"
                className={`sidebar__link ${isNotesActive ? "sidebar__link--active" : ""}`}
              >
                📖 {t("nav.learningNotes")}
              </Link>
            </li>
            <li>
              <Link
                to={`/?source=${FOUNDATIONS_SOURCES}`}
                className={`sidebar__link ${
                  (searchParams.get("source") ?? "") === FOUNDATIONS_SOURCES
                    ? "sidebar__link--active"
                    : ""
                }`}
              >
                {t("nav.foundations")}
              </Link>
            </li>
            <li>
              <Link
                to="/thirty-days"
                className={`sidebar__link ${location.pathname === "/thirty-days" ? "sidebar__link--active" : ""}`}
              >
                {t("nav.thirtyDays")}
              </Link>
            </li>
            <li>
              <Link
                to="/?source=42_python_piscine"
                className={`sidebar__link ${
                  (searchParams.get("source") ?? "") === "42_python_piscine"
                    ? "sidebar__link--active"
                    : ""
                }`}
              >
                {t("nav.piscine")}
              </Link>
            </li>
            <li>
              <Link
                to="/exam"
                className={`sidebar__link ${isExamActive ? "sidebar__link--active" : ""}`}
              >
                🎓 {t("nav.timedExam")}
              </Link>
            </li>
          </ul>
        )}
      </div>

      <div className="sidebar__section">
        <button
          type="button"
          className="sidebar__section-toggle"
          onClick={() => setSqlOpen((open) => !open)}
          aria-expanded={sqlOpen}
        >
          <span className="sidebar__section-title">{t("nav.sql")}</span>
          <span className={`sidebar__chevron ${sqlOpen ? "sidebar__chevron--open" : ""}`}>
            ▸
          </span>
        </button>
        {sqlOpen && (
          <ul className="sidebar__list sidebar__list--nested">
            <li>
              <Link
                to="/sql/notes"
                className={`sidebar__link ${isSqlNotesActive ? "sidebar__link--active" : ""}`}
              >
                📖 {t("nav.sqlNotes")}
              </Link>
            </li>
            {SQL_MODULES.map((mod) => (
              <li key={mod.id}>
                <Link
                  to={`/sql?module=${mod.id}`}
                  className={`sidebar__link ${
                    location.pathname === "/sql" && searchParams.get("module") === mod.id
                      ? "sidebar__link--active"
                      : ""
                  }`}
                >
                  {mod.label}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="sidebar__section">
        <p className="sidebar__section-title">{t("nav.interviews")}</p>
        <ul className="sidebar__list">
          <li>
            <span className="sidebar__link sidebar__link--disabled">
              {t("nav.leetcode")}
              <span className="sidebar__tag">{t("nav.comingSoon")}</span>
            </span>
          </li>
        </ul>
      </div>

      <div className="sidebar__section">
        <p className="sidebar__section-title">{t("nav.comingSoon")}</p>
        <ul className="sidebar__list">
          {COMING_SOON.map((label) => (
            <li key={label}>
              <span className="sidebar__link sidebar__link--disabled">{label}</span>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
