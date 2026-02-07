import { NextResponse } from "next/server";
import { startSurvey } from "@/lib/backend/client";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const questions = Array.isArray(body.questions) ? body.questions : [];
    const trimmed = questions.filter((q: unknown) => typeof q === "string" && q.trim()).map((q: string) => q.trim());
    if (trimmed.length === 0) {
      return NextResponse.json(
        { error: "At least one question is required" },
        { status: 400 }
      );
    }
    const result = await startSurvey(trimmed);
    return NextResponse.json(result);
  } catch (err) {
    console.error("Survey start error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Start failed" },
      { status: 500 }
    );
  }
}
