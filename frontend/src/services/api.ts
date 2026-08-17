import type {
  ExerciseDetail,
  ExerciseSummary,
  HintResponse,
  ProgressItem,
  SolutionResponse,
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
  listExercises: (module?: string) =>
    request<ExerciseSummary[]>(
      module ? `/exercises?module=${encodeURIComponent(module)}` : "/exercises",
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

  saveExplanation: (id: string, text: string) =>
    request<void>(`/exercises/${id}/explanation`, {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  listProgress: () => request<ProgressItem[]>("/progress"),
};
