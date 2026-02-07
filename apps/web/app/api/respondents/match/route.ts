import { NextResponse } from "next/server";

// Mock: return a deterministic count based on demographics for demo.
function mockCount(demographics: Record<string, unknown>): number {
  let base = 42;
  if (demographics.ageRange) base += 8;
  if (demographics.location) base += 12;
  if (Array.isArray(demographics.occupation) && demographics.occupation.length > 0) {
    base += 5 * demographics.occupation.length;
  }
  return Math.min(120, base);
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const demographics = body.demographics ?? {};
    const count = mockCount(demographics);
    return NextResponse.json({
      count,
      tierDistribution: {
        community_voice: Math.floor(count * 0.5),
        active_contributor: Math.floor(count * 0.35),
        community_expert: Math.floor(count * 0.15),
      },
    });
  } catch {
    return NextResponse.json({ count: 0, tierDistribution: {} }, { status: 200 });
  }
}
