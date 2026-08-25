import type {
  ExamResult,
  ExamSessionResponse,
  ExerciseDetail,
  ExerciseSummary,
  FunctionReferenceDetail,
  FunctionReferenceSummary,
  HintResponse,
  LearningNoteDetail,
  LearningNoteSummary,
  ProgressItem,
  SolutionResponse,
  SqlExerciseDetail,
  SqlExerciseSummary,
  SqlHintResponse,
  SqlLearningNoteDetail,
  SqlLearningNoteSummary,
  SqlSolutionResponse,
  SqlSubmissionResult,
  SubmissionResult,
} from "../types/exercise";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Request to ${path} failed (${response.status}): ${body}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  listExercises: (params?: { module?: string; source?: string }) => {
    const query = new URLSearchParams();
    if (params?.module) query.set("module", params.module);
    if (params?.source) query.set("source", params.source);
    const qs = query.toString();
    return request<ExerciseSummary[]>(`/exercises${qs ? `?${qs}` : ""}`);
  },

  getRepeatQueue: () => request<ExerciseSummary[]>("/exercises/repeat-queue"),

  getNextExercise: (source?: string) =>
    request<ExerciseSummary | null>(
      `/exercises/next${source ? `?source=${source}` : ""}`,
    ),

  getExercise: (id: string) => request<ExerciseDetail>(`/exercises/${id}`),

  requestHint: (id: string) =>
    request<HintResponse>(`/exercises/${id}/hint`, { method: "POST" }),

  revealSolution: (id: string) =>
    request<SolutionResponse>(`/exercises/${id}/solution`, { method: "POST" }),

  submit: (id: string, code: string) =>
    request<SubmissionResult>(`/exercises/${id}/submit`, {
      method: "POST",
      body: JSON.stringify({ code }),
    }),

  markRepeat: (id: string) =>
    request<void>(`/exercises/${id}/repeat`, { method: "POST" }),

  saveExplanation: (id: string, text: string) =>
    request<void>(`/exercises/${id}/explanation`, {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  listProgress: () => request<ProgressItem[]>("/progress"),

  listNotes: () => request<LearningNoteSummary[]>("/notes"),

  getNote: (id: string) => request<LearningNoteDetail>(`/notes/${id}`),

  listFunctions: () => request<FunctionReferenceSummary[]>("/functions"),

  getFunction: (id: string) => request<FunctionReferenceDetail>(`/functions/${id}`),

  // --- SQL (Sprint 4) ---

  listSqlExercises: (module?: string) =>
    request<SqlExerciseSummary[]>(`/sql/exercises${module ? `?module=${module}` : ""}`),

  getSqlExercise: (id: string) => request<SqlExerciseDetail>(`/sql/exercises/${id}`),

  requestSqlHint: (id: string) =>
    request<SqlHintResponse>(`/sql/exercises/${id}/hint`, { method: "POST" }),

  revealSqlSolution: (id: string) =>
    request<SqlSolutionResponse>(`/sql/exercises/${id}/solution`, { method: "POST" }),

  submitSql: (id: string, query: string) =>
    request<SqlSubmissionResult>(`/sql/exercises/${id}/submit`, {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  listSqlProgress: () => request<ProgressItem[]>("/sql/progress"),

  listSqlNotes: () => request<SqlLearningNoteSummary[]>("/sql/notes"),

  getSqlNote: (id: string) => request<SqlLearningNoteDetail>(`/sql/notes/${id}`),

  // --- Timed Exam (Sprint 4) ---

  startExam: () => request<ExamSessionResponse>("/exam/start", { method: "POST" }),

  getExamSession: (sessionId: string) =>
    request<ExamSessionResponse>(`/exam/${sessionId}`),

  submitExam: (sessionId: string, answers: Record<string, string>) =>
    request<ExamResult>(`/exam/${sessionId}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),
};
