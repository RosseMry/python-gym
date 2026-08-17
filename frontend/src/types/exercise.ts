export interface ExerciseSummary {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  concepts: string[];
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
}

export interface SubmissionResult {
  passed: boolean;
  tests_total: number;
  tests_passed: number;
  stdout: string;
  stderr: string;
  error: string | null;
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
  | "SOLVED_WITH_HINT"
  | "SOLVED"
  | "MASTERED";

export interface ProgressItem {
  exercise_id: string;
  status: ProgressStatus;
  attempts: number;
  hints_used: number;
  solution_revealed: boolean;
}
