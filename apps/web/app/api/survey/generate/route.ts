import { NextResponse } from "next/server";
import { generateQuestions } from "@/lib/gemini/client";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const objective = typeof body.objective === "string" ? body.objective : "";
    const demographics = body.demographics ?? null;
    if (!objective.trim()) {
      return NextResponse.json(
        { error: "objective is required" },
        { status: 400 }
      );
    }
    const questions = await generateQuestions(objective, demographics);
    return NextResponse.json({ questions });
  } catch (err) {
    console.error("Survey generate error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Generation failed" },
      { status: 500 }
    );
  }
}
