"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { cn } from "@/lib/utils/cn";

interface QuestionEditorProps {
  questions: string[];
  onChange: (questions: string[]) => void;
  onGenerate?: () => void;
  generating?: boolean;
  className?: string;
}

export function QuestionEditor({
  questions,
  onChange,
  onGenerate,
  generating = false,
  className,
}: QuestionEditorProps) {
  const [editingId, setEditingId] = useState<number | null>(null);

  function updateQuestion(index: number, value: string) {
    const next = [...questions];
    next[index] = value;
    onChange(next);
  }

  function removeQuestion(index: number) {
    onChange(questions.filter((_, i) => i !== index));
    setEditingId(null);
  }

  function addQuestion() {
    onChange([...questions, ""]);
    setEditingId(questions.length);
  }

  return (
    <Card className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <p className="text-[11px] tracking-[0.1em] uppercase text-slate-400 font-mono">
          Survey questions
        </p>
        <div className="flex gap-2">
          {onGenerate && (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={onGenerate}
              disabled={generating}
            >
              {generating ? "Generating…" : "Generate with AI"}
            </Button>
          )}
          <Button type="button" variant="secondary" size="sm" onClick={addQuestion}>
            Add question
          </Button>
        </div>
      </div>
      <ul className="space-y-3">
        {questions.map((q, i) => (
          <li key={i} className="flex gap-2 items-start">
            <span className="text-slate-400 text-[13px] font-mono mt-3 shrink-0">
              {i + 1}.
            </span>
            {editingId === i ? (
              <div className="flex-1 flex gap-2">
                <Input
                  value={q}
                  onChange={(e) => updateQuestion(i, e.target.value)}
                  onBlur={() => setEditingId(null)}
                  autoFocus
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeQuestion(i)}
                >
                  Remove
                </Button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setEditingId(i)}
                className="flex-1 text-left text-[14px] text-slate-700 py-2 px-3 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-200"
              >
                {q || "(Empty question)"}
              </button>
            )}
          </li>
        ))}
      </ul>
    </Card>
  );
}
