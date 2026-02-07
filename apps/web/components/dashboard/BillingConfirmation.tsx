"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

// Mock: ~$15 per respondent for demo
const MOCK_COST_PER_RESPONDENT = 15;

interface BillingConfirmationProps {
  questionCount: number;
  respondentCount: number;
  onStart: (respondentCount: number) => Promise<void>;
  disabled?: boolean;
  className?: string;
}

export function BillingConfirmation({
  questionCount,
  respondentCount: initialCount,
  onStart,
  disabled = false,
  className,
}: BillingConfirmationProps) {
  const [respondentCount, setRespondentCount] = useState(initialCount || 10);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const costEstimate = respondentCount * MOCK_COST_PER_RESPONDENT;

  async function handleConfirm() {
    setError(null);
    setLoading(true);
    try {
      await onStart(respondentCount);
      setDone(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <Card className={className}>
        <p className="text-[11px] tracking-[0.1em] uppercase text-slate-400 font-mono mb-2">
          Status
        </p>
        <p className="text-slate-700">Survey started. First question sent to WhatsApp.</p>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <p className="text-[11px] tracking-[0.1em] uppercase text-slate-400 font-mono mb-2">
        Cost estimate (demo)
      </p>
      <p className="text-slate-600 text-[14px] mb-4">
        {questionCount} questions × {respondentCount} respondents ≈ ${costEstimate} (mock rate)
      </p>
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <label className="text-[13px] text-slate-600">Number of respondents:</label>
        <Input
          type="number"
          min={1}
          max={500}
          value={respondentCount}
          onChange={(e) => setRespondentCount(parseInt(e.target.value, 10) || 10)}
          className="w-24"
        />
      </div>
      {error && <p className="text-red-600 text-[13px] mb-2">{error}</p>}
      <Button onClick={handleConfirm} disabled={disabled || loading}>
        {loading ? "Starting…" : "Start survey"}
      </Button>
    </Card>
  );
}
