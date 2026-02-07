import { GoogleGenerativeAI } from "@google/generative-ai";
import { QUESTION_GENERATION_PROMPT } from "./prompts";
import { extractionSchema, type ExtractionOutput } from "./types";

const apiKey = process.env.GOOGLE_GEMINI_API_KEY ?? process.env.GEMINI_API_KEY;

function getModel() {
  if (!apiKey) {
    throw new Error("Missing GOOGLE_GEMINI_API_KEY or GEMINI_API_KEY");
  }
  return new GoogleGenerativeAI(apiKey).getGenerativeModel({
    model: "gemini-2.0-flash",
  });
}

export async function generateChatResponse(
  systemPrompt: string,
  messages: Array<{ role: "user" | "assistant"; content: string }>
): Promise<string> {
  const model = getModel();
  const last = messages[messages.length - 1];
  if (!last || last.role !== "user") {
    throw new Error("Last message must be from user");
  }
  const history = messages.slice(0, -1).map((m) => ({
    role: m.role === "user" ? "user" : "model",
    parts: [{ text: m.content }],
  }));
  const chat = model.startChat({
    systemInstruction: systemPrompt,
    history,
  });
  const result = await chat.sendMessage(last.content);
  const response = result.response;
  const text = response.text();
  if (!text) throw new Error("Empty Gemini response");
  return text;
}

const JSON_BLOCK_REGEX = /```(?:json)?\s*([\s\S]*?)```/;

export function parseExtractionFromResponse(responseText: string): ExtractionOutput | null {
  const match = responseText.match(JSON_BLOCK_REGEX);
  const raw = match?.[1];
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw.trim()) as unknown;
    return extractionSchema.parse(parsed) as ExtractionOutput;
  } catch {
    return null;
  }
}

export async function generateQuestions(objective: string, demographics: Record<string, unknown> | null): Promise<string[]> {
  const model = getModel();
  const prompt = `${QUESTION_GENERATION_PROMPT}\n\nObjective: ${objective}\nDemographics: ${JSON.stringify(demographics ?? {})}`;
  const result = await model.generateContent(prompt);
  const text = result.response.text();
  if (!text) throw new Error("Empty question generation response");
  const match = text.match(JSON_BLOCK_REGEX);
  const raw = match?.[1]?.trim() ?? text.trim();
  const parsed = JSON.parse(raw) as unknown;
  if (!Array.isArray(parsed)) throw new Error("Expected array of questions");
  return parsed.filter((q): q is string => typeof q === "string" && q.length > 0);
}
