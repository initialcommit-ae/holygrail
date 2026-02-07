"use client";

import { useState, useCallback } from "react";
import { Link } from "@/i18n/routing";
import { ChatInterface } from "@/components/dashboard/ChatInterface";
import { DemographicsSummary } from "@/components/dashboard/DemographicsSummary";
import { RespondentMatcher } from "@/components/dashboard/RespondentMatcher";
import { QuestionEditor } from "@/components/dashboard/QuestionEditor";
import { BillingConfirmation } from "@/components/dashboard/BillingConfirmation";
import type { Demographics } from "@/types/chat";
import { cn } from "@/lib/utils/cn";

export default function DashboardPage() {
  const [demographics, setDemographics] = useState<Demographics | null>(null);
  const [objective, setObjective] = useState<string | null>(null);
  const [matchCount, setMatchCount] = useState<number | null>(null);
  const [tierDistribution, setTierDistribution] = useState<Record<string, number> | null>(null);
  const [ready, setReady] = useState(false);
  const [questions, setQuestions] = useState<string[]>([]);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [sidebarSection, setSidebarSection] = useState<"new" | "past" | "conversation">("new");

  const handleDemographicsExtracted = useCallback(
    async (d: Demographics, obj: string) => {
      setDemographics(d);
      setObjective(obj);
      try {
        const res = await fetch("/api/respondents/match", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ demographics: d }),
        });
        const data = await res.json();
        setMatchCount(data.count ?? 0);
        setTierDistribution(data.tierDistribution ?? null);
      } catch {
        setMatchCount(42);
      }
    },
    []
  );

  const handleGenerateQuestions = useCallback(async () => {
    if (!objective) return;
    setGeneratingQuestions(true);
    try {
      const res = await fetch("/api/survey/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ objective, demographics: demographics ?? {} }),
      });
      const data = await res.json();
      if (data.questions?.length) setQuestions(data.questions);
    } catch {
      setQuestions([]);
    } finally {
      setGeneratingQuestions(false);
    }
  }, [objective, demographics]);

  const handleStartSurvey = useCallback(async (_respondentCount: number) => {
    const qs = questions.filter((q) => q.trim());
    if (qs.length === 0) throw new Error("Add at least one question");
    const res = await fetch("/api/survey/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questions: qs }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to start");
  }, [questions]);

  return (
    <div className="min-h-screen bg-[var(--bg-color)] text-[var(--text-color)] flex">
      {/* Sidebar */}
      <aside className="w-56 shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <div className="p-6 border-b border-slate-100">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-black" />
            <span className="text-xl tracking-tight font-mono">MeshAi</span>
          </Link>
        </div>
        <nav className="p-4 space-y-1">
          <button
            onClick={() => setSidebarSection("new")}
            className={cn(
              "w-full text-left px-4 py-3 rounded-xl text-[14px] transition-colors",
              sidebarSection === "new"
                ? "bg-black text-white font-mono"
                : "text-slate-600 hover:bg-slate-100"
            )}
          >
            Create new survey
          </button>
          <button
            onClick={() => setSidebarSection("past")}
            className={cn(
              "w-full text-left px-4 py-3 rounded-xl text-[14px] transition-colors",
              sidebarSection === "past"
                ? "bg-black text-white font-mono"
                : "text-slate-600 hover:bg-slate-100"
            )}
          >
            View past surveys
          </button>
          <button
            onClick={() => setSidebarSection("conversation")}
            className={cn(
              "w-full text-left px-4 py-3 rounded-xl text-[14px] transition-colors",
              sidebarSection === "conversation"
                ? "bg-black text-white font-mono"
                : "text-slate-600 hover:bg-slate-100"
            )}
          >
            Your conversation
          </button>
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="border-b border-slate-200 bg-white px-8 py-4">
          <h1 className="text-2xl font-mono text-slate-900 light-heading">
            {sidebarSection === "new" && "Create New Study"}
            {sidebarSection === "past" && "Past Surveys"}
            {sidebarSection === "conversation" && "Your Conversation"}
          </h1>
        </header>

        <div className="flex-1 overflow-hidden flex flex-col">
          {sidebarSection === "past" && (
            <div className="p-8 text-slate-500 text-[14px]">
              No past surveys yet. Create one to see it here.
            </div>
          )}

          {sidebarSection === "conversation" && (
            <div className="flex-1 flex flex-col max-w-2xl mx-auto w-full border-x border-slate-200 bg-white">
              <ChatInterface />
            </div>
          )}

          {sidebarSection === "new" && (
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-3xl mx-auto p-8 space-y-8">
                {/* Chat + demographics + match */}
                <section className="space-y-4">
                  <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden min-h-[320px] flex flex-col">
                    <ChatInterface
                      onDemographicsExtracted={handleDemographicsExtracted}
                      onReady={setReady}
                    />
                  </div>
                  {demographics && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <DemographicsSummary demographics={demographics} />
                      {matchCount !== null && (
                        <RespondentMatcher
                          count={matchCount}
                          tierDistribution={tierDistribution ?? undefined}
                        />
                      )}
                    </div>
                  )}
                </section>

                {/* Questions */}
                {(ready || questions.length > 0) && (
                  <section>
                    <QuestionEditor
                      questions={questions}
                      onChange={setQuestions}
                      onGenerate={handleGenerateQuestions}
                      generating={generatingQuestions}
                    />
                  </section>
                )}

                {/* Billing + Start */}
                {questions.length > 0 && (
                  <section>
                    <BillingConfirmation
                      questionCount={questions.filter((q) => q.trim()).length}
                      respondentCount={matchCount ?? 10}
                      onStart={handleStartSurvey}
                    />
                  </section>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
