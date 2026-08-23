import { Link, useLocation } from "react-router-dom";
import "./Sidebar.css";

interface SidebarProps {
  repeatCount: number;
}

const PYTHON_SOURCES: { label: string; source: string }[] = [
  { label: "Foundations", source: "progressive_python" },
  { label: "30 Days of Python", source: "30_days_of_python" },
  { label: "42 Python Piscine", source: "42_python_piscine" },
];

const COMING_SOON = ["SQL", "Data Science", "Mathematics", "Machine Learning", "ML Piscine"];

/**
 * The learning-track sidebar (Sprint 2 spec section 35). Only the
 * Python track and repeat queue are wired to real data this sprint -
 * Interviews and Coming Soon are shown, disabled, to set expectations
 * for what's next without pretending they're implemented.
 */
export function Sidebar({ repeatCount }: SidebarProps) {
  const location = useLocation();

  return (
    <nav className="sidebar">
      <Link to="/" className="sidebar__brand">
        Python Gym
      </Link>

      {repeatCount > 0 && (
        <Link
          to="/repeat"
          className={`sidebar__repeat ${location.pathname === "/repeat" ? "sidebar__repeat--active" : ""}`}
        >
          🔁 Repeat queue
          <span className="sidebar__badge">{repeatCount}</span>
        </Link>
      )}

      <div className="sidebar__section">
        <p className="sidebar__section-title">Python</p>
        <ul className="sidebar__list">
          {PYTHON_SOURCES.map(({ label, source }) => {
            const to = `/?source=${source}`;
            const active = location.search === `?source=${source}`;
            return (
              <li key={source}>
                <Link
                  to={to}
                  className={`sidebar__link ${active ? "sidebar__link--active" : ""}`}
                >
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="sidebar__section">
        <p className="sidebar__section-title">Interviews</p>
        <ul className="sidebar__list">
          <li>
            <span className="sidebar__link sidebar__link--disabled">
              LeetCode Top Interview 150
              <span className="sidebar__tag">Coming soon</span>
            </span>
          </li>
        </ul>
      </div>

      <div className="sidebar__section">
        <p className="sidebar__section-title">Coming soon</p>
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
