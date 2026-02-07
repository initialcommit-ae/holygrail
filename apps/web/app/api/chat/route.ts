import { NextResponse } from "next/server";
import { SYSTEM_PROMPT } from "@/lib/gemini/prompts";
import { generateChatResponse, parseExtractionFromResponse } from "@/lib/gemini/client";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const messages = Array.isArray(body.messages) ? body.messages : [];
    if (messages.length === 0) {
      return NextResponse.json(
        { error: "messages array required" },
        { status: 400 }
      );
    }
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage || lastMessage.role !== "user") {
      return NextResponse.json(
        { error: "Last message must be from user" },
        { status: 400 }
      );
    }

    const responseText = await generateChatResponse(SYSTEM_PROMPT, messages);
    const extraction = parseExtractionFromResponse(responseText);

    const message = responseText.replace(/```json[\s\S]*?```/g, "").trim();

    return NextResponse.json({
      message,
      demographics: extraction?.demographics,
      ready: extraction?.ready ?? false,
      objective: extraction?.objective,
    });
  } catch (err) {
    console.error("Chat API error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Chat failed" },
      { status: 500 }
    );
  }
}
