export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: Date;
}

export interface Demographics {
  ageRange?: string;
  location?: string;
  occupation?: string[];
}

export interface ChatState {
  messages: ChatMessage[];
  demographics: Demographics | null;
  matchCount: number | null;
  ready: boolean;
  objective: string | null;
}
