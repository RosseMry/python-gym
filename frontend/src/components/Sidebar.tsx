import { Link, useLocation, useSearchParams } from "react-router-dom";
import { useLocale } from "../i18n/LocaleContext";
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
  const [searchParams] = useSearchParams();
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
        <p className="sidebar__section-title">{t("nav.progressive")}</p>
        <ul className="sidebar__list">
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
              to="/notes"
              className={`sidebar__link ${location.pathname.startsWith("/notes") ? "sidebar__link--active" : ""}`}
            >
              📖 {t("nav.learningNotes")}
            </Link>
          </li>
        </ul>
      </div>

      <div className="sidebar__section">
        <p className="sidebar__section-title">{t("nav.piscine")}</p>
        <ul className="sidebar__list">
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
        </ul>
      </div>

      <div className="sidebar__section">
        <p className="sidebar__section-title">{t("nav.exam")}</p>
        <ul className="sidebar__list">
          <li>
            <span className="sidebar__link sidebar__link--disabled">
              {t("nav.pythonExam")}
              <span className="sidebar__tag">{t("nav.comingSoon")}</span>
            </span>
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
