export interface ExerciseSummary {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  title_fr: string | null;
  concepts: string[];
  track: string;
  source: string;
  exercise_type: string;
  exercise_status: string;
  day: number | null;
  level: number | null;
}

export interface Prerequisite {
  id: string;
  title: string;
  solved: boolean;
}

export interface ExerciseDetail {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  title_fr: string | null;
  description: string;
  description_fr: string | null;
  examples: string;
  examples_fr: string | null;
  starter_code: string;
  expected_behavior: string;
  expected_behavior_fr: string | null;
  concepts: string[];
  track: string;
  source: string;
  skills: string[];
  prerequisites: Prerequisite[];
  resources: string[];
  validation_profile: string;
  exercise_type: string;
  exercise_status: string;
  day: number | null;
  level: number | null;
}

export interface TestOutcome {
  label: string;
  passed: boolean;
  detail: string;
}

export interface StyleCheckResult {
  ran: boolean;
  passed: boolean;
  output: string;
}

export interface SubmissionResult {
  status: "passed" | "failed" | "error";
  passed: boolean;
  tests_total: number;
  tests_passed: number;
  tests: TestOutcome[];
  stdout: string;
  stderr: string;
  result: string | null;
  execution_time: number;
  error: string | null;
  style: StyleCheckResult | null;
}

export interface HintResponse {
  hint: string;
  hint_fr: string | null;
}

export interface SolutionResponse {
  solution: string;
  explanation: string;
  explanation_fr: string | null;
}

export interface LearningNoteSummary {
  id: string;
  module: string;
  title: string;
  title_fr: string | null;
}

export interface LearningNoteDetail {
  id: string;
  module: string;
  title: string;
  title_fr: string | null;
  explanation: string;
  explanation_fr: string | null;
  syntax: string;
  syntax_fr: string | null;
  examples: string;
  examples_fr: string | null;
  common_mistakes: string;
  common_mistakes_fr: string | null;
  mini_exercise: string;
  mini_exercise_fr: string | null;
  related_exercise_ids: string[];
}

export type ProgressStatus =
  | "NEW"
  | "ATTEMPTED"
  | "FAILED"
  | "SOLVED_WITH_HINT"
  | "SOLVED_AFTER_SOLUTION"
  | "SOLVED"
  | "SOLVED_TO_REPEAT"
  | "MASTERED";

export interface ProgressItem {
  exercise_id: string;
  status: ProgressStatus;
  attempts: number;
  hints_used: number;
  solution_revealed: boolean;
}

// Content sources, matching the backend's `source` field (Sprint 2 spec
// section 18). Used to group the sidebar and filter exercise lists.
export const CONTENT_SOURCES = {
  foundations: "Foundations",
  progressive_python: "Progressive Python",
  python_gym: "Python-Gym Exercises",
  "30_days_of_python": "30 Days of Python",
  "42_python_piscine": "42 Python Piscine",
} as const;

export type ContentSource = keyof typeof CONTENT_SOURCES;
