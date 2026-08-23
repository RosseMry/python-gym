import { Link, useLocation } from "react-router-dom";
import { CONTENT_SOURCES } from "../types/exercise";
import { useLocale } from "../i18n/LocaleContext";
import "./Sidebar.css";

interface SidebarProps {
  repeatCount: number;
}

// Display order for the Python sub-sections - derived from
// CONTENT_SOURCES (the single source of truth for source -> label) so
// the two never drift apart, with a translation-key per source for the
// nav (CONTENT_SOURCES itself stays English-only, used as an API
// fallback label).
const PYTHON_SOURCES: { source: keyof typeof CONTENT_SOURCES; labelKey: string }[] = [
  { source: "foundations", labelKey: "nav.foundations" },
  { source: "progressive_python", labelKey: "nav.progressivePython" },
  { source: "python_gym", labelKey: "nav.pythonGym" },
  { source: "30_days_of_python", labelKey: "nav.thirtyDays" },
  { source: "42_python_piscine", labelKey: "nav.piscine" },
];

const COMING_SOON = ["SQL", "Data Science", "Mathematics", "Machine Learning", "ML Piscine"];

/**
 * The learning-track sidebar (Sprint 2 spec section 35, extended in
 * Sprint 3 with Foundations/Python-Gym/Learning Notes and a language
 * toggle). Only the Python track and repeat queue are wired to real
 * data - Interviews and Coming Soon are shown, disabled, to set
 * expectations for what's next without pretending they're implemented.
 */
export function Sidebar({ repeatCount }: SidebarProps) {
  const location = useLocation();
  const { locale, setLocale, t } = useLocale();

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
        <p className="sidebar__section-title">{t("nav.python")}</p>
        <ul className="sidebar__list">
          {PYTHON_SOURCES.map(({ source, labelKey }) => {
            const to = `/?source=${source}`;
            const active = location.search === `?source=${source}`;
            return (
              <li key={source}>
                <Link
                  to={to}
                  className={`sidebar__link ${active ? "sidebar__link--active" : ""}`}
                >
                  {t(labelKey)}
                </Link>
              </li>
            );
          })}
          <li>
            <Link
              to="/notes"
              className={`sidebar__link ${location.pathname.startsWith("/notes") ? "sidebar__link--active" : ""}`}
            >
              📖 {t("nav.learningNotes")}
            </Link>
          </li>
        </ul>
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
