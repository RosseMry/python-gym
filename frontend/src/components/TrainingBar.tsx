import type { ProgressStatus } from "../types/exercise";
import "./TrainingBar.css";

interface Rep {
  id: string;
  status: ProgressStatus;
}

interface TrainingBarProps {
  label: string;
  reps: Rep[];
}

const STATUS_ORDER: Record<ProgressStatus, number> = {
  NEW: 0,
  ATTEMPTED: 1,
  FAILED: 1,
  SOLVED_WITH_HINT: 2,
  SOLVED: 3,
  SOLVED_TO_REPEAT: 3,
  MASTERED: 4,
};

/**
 * The "signature" visual: each exercise in a module renders as one
 * plate on a barbell. An unattempted exercise is an empty ring; a
 * mastered one is a full, solid plate. It's a literal training bar
 * for a "Python Gym" - progress you can see building up rep by rep.
 */
export function TrainingBar({ label, reps }: TrainingBarProps) {
  const solvedCount = reps.filter(
    (r) => STATUS_ORDER[r.status] >= STATUS_ORDER.SOLVED,
  ).length;

  return (
    <div className="training-bar">
      <div className="training-bar__label">
        <span>{label}</span>
        <span className="training-bar__count">
          {solvedCount}/{reps.length}
        </span>
      </div>
      <div className="training-bar__rack" role="img" aria-label={`${label}: ${solvedCount} of ${reps.length} solved`}>
        <div className="training-bar__sleeve training-bar__sleeve--left" />
        {reps.map((rep) => (
          <div
            key={rep.id}
            className={`training-bar__plate training-bar__plate--${rep.status.toLowerCase()}`}
          />
        ))}
        <div className="training-bar__sleeve training-bar__sleeve--right" />
      </div>
    </div>
  );
}
