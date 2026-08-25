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
  hint_function: string | null;
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

export interface FunctionReferenceSummary {
  id: string;
  name: string;
  name_fr: string | null;
}

export interface FunctionReferenceDetail {
  id: string;
  name: string;
  name_fr: string | null;
  what_it_does: string;
  what_it_does_fr: string | null;
  syntax: string;
  parameters: string;
  parameters_fr: string | null;
  return_value: string;
  return_value_fr: string | null;
  example: string;
  example_output: string;
  common_mistakes: string;
  common_mistakes_fr: string | null;
  when_to_use: string;
  when_to_use_fr: string | null;
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

// ---------------------------------------------------------------------
// Sprint 4: SQL
// ---------------------------------------------------------------------

export const SQL_MODULES: { id: string; label: string }[] = [
  { id: "foundations", label: "Foundations" },
  { id: "relational", label: "Relational Concepts" },
  { id: "joins", label: "JOINs" },
  { id: "intermediate", label: "Intermediate SQL" },
  { id: "window", label: "Window Functions" },
  { id: "dbops", label: "Database Operations" },
  { id: "views", label: "Views" },
  { id: "transactions", label: "Transactions" },
  { id: "indexes", label: "Indexes" },
  { id: "functions", label: "Functions" },
  { id: "procedures", label: "Procedures" },
  { id: "triggers", label: "Triggers" },
];

// Mini Project id -> display label. New projects just need an entry
// here (and their own resources/sql/<project>_fixtures.sql + JSON
// exercise files) - no other frontend change needed to appear in the
// Mini Projects list, since project ids themselves come from the API
// (GET /api/sql/exercises/projects/list).
export const MINI_PROJECT_LABELS: Record<string, string> = {
  ecommerce_sales_analysis: "E-Commerce Sales Analysis",
};

export interface SqlExerciseSummary {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  source: string;
  project: string | null;
  part: number | null;
}

export interface SqlExerciseDetail {
  id: string;
  module: string;
  difficulty: number;
  title: string;
  title_fr: string | null;
  description: string;
  description_fr: string | null;
  starter_query: string;
  expected_behavior: string;
  concepts: string[];
  skills: string[];
  source: string;
  postgres_note: string | null;
  prerequisites: string[];
  project: string | null;
  part: number | null;
}

export interface SqlHintResponse {
  hint: string;
  hint_fr: string | null;
}

export interface SqlSolutionResponse {
  solution: string;
  explanation: string;
}

export interface SqlSubmissionResult {
  status: "passed" | "failed" | "error";
  passed: boolean;
  tests_total: number;
  tests_passed: number;
  tests: TestOutcome[];
  result_columns: string[];
  result_rows: string[][];
  error: string | null;
  execution_time: number;
}

export interface SqlLearningNoteSummary {
  id: string;
  module: string;
  title: string;
  title_fr: string | null;
}

export interface SqlLearningNoteDetail {
  id: string;
  module: string;
  title: string;
  title_fr: string | null;
  what_is_it: string;
  what_is_it_fr: string | null;
  why_it_matters: string;
  why_it_matters_fr: string | null;
  syntax: string;
  syntax_fr: string | null;
  example: string;
  output: string;
  common_mistakes: string;
  common_mistakes_fr: string | null;
  postgres_note: string | null;
  mini_exercise: string;
  mini_exercise_fr: string | null;
  source: string;
  related_exercise_ids: string[];
}

// ---------------------------------------------------------------------
// Sprint 4: Timed Exam
// ---------------------------------------------------------------------

export interface ExamQuestionForStudent {
  id: string;
  kind: "mcq" | "output_prediction" | "debugging" | "coding";
  category: string;
  prompt: string;
  points: number;
  code_snippet: string | null;
  starter_code: string | null;
  choices: string[] | null;
}

export interface ExamSessionResponse {
  session_id: string;
  started_at: string;
  duration_seconds: number;
  deadline_at: string;
  status: string;
  questions: ExamQuestionForStudent[];
}

export interface ExamAnswerResult {
  question_id: string;
  correct: boolean;
  points_earned: number;
  points_possible: number;
}

export interface ExamResult {
  session_id: string;
  status: string;
  score: number;
  max_score: number;
  questions_total: number;
  questions_correct: number;
  time_used_seconds: number;
  answers: ExamAnswerResult[];
}
