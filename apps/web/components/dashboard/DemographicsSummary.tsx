"use client";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { Demographics } from "@/types/chat";

interface DemographicsSummaryProps {
  demographics: Demographics;
  className?: string;
}

export function DemographicsSummary({ demographics, className }: DemographicsSummaryProps) {
  const items: string[] = [];
  if (demographics.ageRange) items.push(`Age: ${demographics.ageRange}`);
  if (demographics.location) items.push(`Location: ${demographics.location}`);
  if (demographics.occupation?.length) {
    items.push(`Occupation: ${demographics.occupation.join(", ")}`);
  }
  if (items.length === 0) return null;

  return (
    <Card className={className}>
      <p className="text-[11px] tracking-[0.1em] uppercase text-slate-400 mb-2 font-mono">
        Target demographics
      </p>
      <div className="flex flex-wrap gap-2">
        {items.map((label) => (
          <Badge key={label}>{label}</Badge>
        ))}
      </div>
    </Card>
  );
}
