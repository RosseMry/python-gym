export interface ExerciseSummary {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  concepts: string[];
  track: string;
  source: string;
  exercise_type: string;
}

export interface ExerciseDetail {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  description: string;
  examples: string;
  starter_code: string;
  expected_behavior: string;
  concepts: string[];
  track: string;
  source: string;
  skills: string[];
  prerequisites: string[];
  resources: string[];
  validation_profile: string;
  exercise_type: string;
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
}

export interface SolutionResponse {
  solution: string;
  explanation: string;
}

export type ProgressStatus =
  | "NEW"
  | "ATTEMPTED"
  | "FAILED"
  | "SOLVED_WITH_HINT"
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
  progressive_python: "Progressive Python",
  "30_days_of_python": "30 Days of Python",
  "42_python_piscine": "42 Python Piscine",
} as const;

export type ContentSource = keyof typeof CONTENT_SOURCES;
