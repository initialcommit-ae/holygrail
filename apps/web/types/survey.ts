import type { Demographics } from "./chat";

export interface StartSurveyPayload {
  questions: string[];
}

export interface StartSurveyResponse {
  ok: boolean;
  sent_to?: string;
  question_count?: number;
}

export interface SurveyFlowState {
  objective: string | null;
  demographics: Demographics | null;
  questions: string[];
  respondentCount: number | null;
  costEstimate: number | null;
}
