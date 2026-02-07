import type { StartSurveyResponse } from "@/types/survey";

const BASE = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function startSurvey(questions: string[]): Promise<StartSurveyResponse> {
  const res = await fetch(`${BASE}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ questions }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || data.message || "Failed to start survey");
  }
  return data as StartSurveyResponse;
}
