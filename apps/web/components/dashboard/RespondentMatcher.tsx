"use client";

import { Card } from "@/components/ui/Card";

interface RespondentMatcherProps {
  count: number;
  tierDistribution?: {
    community_voice?: number;
    active_contributor?: number;
    community_expert?: number;
  };
  className?: string;
}

export function RespondentMatcher({ count, tierDistribution, className }: RespondentMatcherProps) {
  return (
    <Card className={className}>
      <p className="text-[11px] tracking-[0.1em] uppercase text-slate-400 mb-1 font-mono">
        Matching respondents
      </p>
      <p className="text-2xl font-mono text-slate-900">{count}</p>
      {tierDistribution && (
        <div className="mt-2 flex flex-wrap gap-2 text-[12px] text-slate-500">
          {tierDistribution.community_voice != null && (
            <span>Voice: {tierDistribution.community_voice}</span>
          )}
          {tierDistribution.active_contributor != null && (
            <span>Contributor: {tierDistribution.active_contributor}</span>
          )}
          {tierDistribution.community_expert != null && (
            <span>Expert: {tierDistribution.community_expert}</span>
          )}
        </div>
      )}
    </Card>
  );
}
