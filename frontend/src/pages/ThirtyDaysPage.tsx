import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import type { ExerciseSummary, ProgressItem } from "../types/exercise";
import { useLocale, useLocalized } from "../i18n/LocaleContext";
import "./ThirtyDaysPage.css";

// Real day topics from github.com/Asabeneh/30-Days-Of-Python, used to
// label every day (even ones with no content yet) so the page shows
// the real Day 01-30 structure the spec asks for, without fabricating
// exercises for days not yet imported.
const DAY_TOPICS: Record<number, string> = {
  1: "Introduction",
  2: "Variables & built-in functions",
  3: "Operators",
  4: "Strings",
  5: "Lists",
  6: "Tuples",
  7: "Sets",
  8: "Dictionaries",
  9: "Conditionals",
  10: "Loops",
  11: "Functions",
  12: "Modules",
  13: "List comprehension",
  14: "Higher-order functions",
  15: "Python type errors",
  16: "Python date time",
  17: "Exception handling",
  18: "Regular expressions",
  19: "File handling",
  20: "Python package manager",
  21: "Classes and objects",
};

// Days 22-29 need live network access, a running database, or a web
// server - none of which fit Python-Gym's local function/script
// grading model. Represented so the real Day 01-30 structure is
// visible, but locked rather than fabricated. Day 30 ("Conclusions")
// has no exercises at all and is omitted entirely.
const LOCKED_DAYS: Record<number, { topic: string; reason: string }> = {
  22: { topic: "Web scraping", reason: "Needs live network access" },
  23: { topic: "Virtual environment", reason: "Tool usage, not a gradable exercise" },
  24: { topic: "Statistics", reason: "Needs a NumPy/Pandas track" },
  25: { topic: "Pandas", reason: "Needs a Pandas track" },
  26: { topic: "Python web", reason: "Needs a running web server" },
  27: { topic: "Python with MongoDB", reason: "Needs a running MongoDB instance" },
  28: { topic: "API", reason: "Needs live network access" },
  29: { topic: "Building API", reason: "Needs a running web server" },
};

interface DayGroup {
  day: number;
  byLevel: Record<string, ExerciseSummary[]>;
}

function groupByDay(exercises: ExerciseSummary[]): DayGroup[] {
  const byDay = new Map<number, Record<string, ExerciseSummary[]>>();
  for (const exercise of exercises) {
    if (exercise.day == null) continue;
    const levels = byDay.get(exercise.day) ?? {};
    const levelKey = exercise.level == null ? "_" : String(exercise.level);
    (levels[levelKey] ??= []).push(exercise);
    byDay.set(exercise.day, levels);
  }
  return [...byDay.entries()]
    .sort(([a], [b]) => a - b)
    .map(([day, byLevel]) => ({ day, byLevel }));
}

export function ThirtyDaysPage() {
  const [exercises, setExercises] = useState<ExerciseSummary[] | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressItem>>({});
  const [error, setError] = useState<string | null>(null);
  const { t } = useLocale();
  const localize = useLocalized();

  useEffect(() => {
    Promise.all([api.listExercises({ source: "30_days_of_python" }), api.listProgress()])
      .then(([exerciseList, progressList]) => {
        setExercises(exerciseList);
        setProgress(Object.fromEntries(progressList.map((p) => [p.exercise_id, p])));
      })
      .catch((e) => setError(String(e)));
  }, []);

  if (error) {
    return (
      <div className="page">
        <p className="error-banner">{error}</p>
      </div>
    );
  }

  if (!exercises) {
    return <div className="page">{t("list.loading")}</div>;
  }

  const groups = groupByDay(exercises);
  const contentDays = new Set(groups.map((g) => g.day));

  return (
    <div className="page thirty-days-page">
      <header className="page-header">
        <p className="eyebrow">{t("nav.progressive")}</p>
        <h1>{t("nav.thirtyDays")}</h1>
        <p className="subtitle">{t("thirtyDays.subtitle")}</p>
      </header>

      <nav className="thirty-days__jump" aria-label="Jump to day">
        {Array.from({ length: 30 }, (_, i) => i + 1).map((day) => {
          const has = contentDays.has(day);
          const locked = day in LOCKED_DAYS;
          return has ? (
            <a key={day} href={`#day-${day}`} className="thirty-days__jump-link">
              {day}
            </a>
          ) : (
            <span
              key={day}
              className={`thirty-days__jump-link thirty-days__jump-link--${locked ? "locked" : "muted"}`}
            >
              {locked ? "🔒" : ""}
              {day}
            </span>
          );
        })}
      </nav>

      {Array.from({ length: 29 }, (_, i) => i + 1).map((day) => {
        const group = groups.find((g) => g.day === day);
        const lockedInfo = LOCKED_DAYS[day];

        if (!group && !lockedInfo) {
          return (
            <div key={day} id={`day-${day}`} className="thirty-days__day thirty-days__day--empty">
              <span className="thirty-days__day-number">Day {String(day).padStart(2, "0")}</span>
              <span className="thirty-days__day-topic">
                {DAY_TOPICS[day] ?? ""} - {t("thirtyDays.notImportedYet")}
              </span>
            </div>
          );
        }

        if (lockedInfo) {
          return (
            <div key={day} id={`day-${day}`} className="thirty-days__day thirty-days__day--locked">
              <span className="thirty-days__day-number">🔒 Day {String(day).padStart(2, "0")}</span>
              <span className="thirty-days__day-topic">
                {lockedInfo.topic} - {lockedInfo.reason}
              </span>
            </div>
          );
        }

        const levelKeys = Object.keys(group!.byLevel).sort((a, b) =>
          a === "_" ? -1 : b === "_" ? 1 : Number(a) - Number(b),
        );
        const allExercises = Object.values(group!.byLevel).flat();
        const solvedCount = allExercises.filter((e) =>
          ["SOLVED", "SOLVED_WITH_HINT", "SOLVED_AFTER_SOLUTION", "SOLVED_TO_REPEAT", "MASTERED"].includes(
            progress[e.id]?.status ?? "NEW",
          ),
        ).length;

        return (
          <details key={day} id={`day-${day}`} className="thirty-days__day">
            <summary className="thirty-days__day-summary">
              <span className="thirty-days__day-number">Day {String(day).padStart(2, "0")}</span>
              <span className="thirty-days__day-topic">{DAY_TOPICS[day] ?? group!.day}</span>
              <span className="thirty-days__day-progress">
                {solvedCount}/{allExercises.length}
              </span>
            </summary>
            {levelKeys.map((levelKey) => (
              <div key={levelKey} className="thirty-days__level">
                {levelKey !== "_" && (
                  <p className="thirty-days__level-title">Level {levelKey}</p>
                )}
                <ul className="exercise-list">
                  {group!.byLevel[levelKey].map((exercise) => {
                    const status = progress[exercise.id]?.status ?? "NEW";
                    return (
                      <li key={exercise.id}>
                        <Link to={`/exercises/${exercise.id}`} className="exercise-card">
                          <span className={`status-dot status-dot--${status.toLowerCase()}`} />
                          <span className="exercise-card__title">
                            {localize(exercise.title, exercise.title_fr)}
                          </span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </details>
        );
      })}
    </div>
  );
}
