"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Heart,
  ShieldAlert,
  DollarSign,
  Send,
  FileText,
} from "lucide-react";

function renderBriefingText(text: string) {
  if (!text) return null;
  const paragraphs = text.split(/\n+/).filter(Boolean);
  return (
    <div className="space-y-6">
      {paragraphs.map((p, idx) => {
        if (p.includes("Executive Briefing —")) {
          return (
            <div key={idx} className="border-b border-slate-100 dark:border-dark-border pb-3">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                {p.replace(/\*\*/g, "")}
              </h3>
            </div>
          );
        }
        if (p.includes("**Risks:**") && p.includes("**Opportunities:**")) {
          const risksPart = p.match(/\*\*Risks:\*\*(.*?)(?=\*\*Opportunities:\*\*|$)/)?.[1]?.trim() || "";
          const oppsPart = p.match(/\*\*Opportunities:\*\*(.*)/)?.[1]?.trim() || "";
          return (
            <div key={idx} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                  Key Risks
                </h4>
                <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {risksPart.replace(/\*\*/g, "")}
                </p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2">
                  Opportunities
                </h4>
                <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {oppsPart.replace(/\*\*/g, "")}
                </p>
              </div>
            </div>
          );
        }
        if (p.includes("**Recommended Actions:**")) {
          const cleanText = p.replace(/\*\*Recommended Actions:\*\*/g, "").trim();
          const items = cleanText.split(/\(\d+\)/).map(item => item.trim()).filter(Boolean);
          return (
            <div key={idx} className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-dark-border dark:bg-dark-bg/60 space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Recommended Actions
              </h4>
              <div className="space-y-2.5">
                {items.map((item, itemIdx) => (
                  <div key={itemIdx} className="flex gap-3 text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-800 dark:bg-white text-xs font-semibold text-white dark:text-slate-900">
                      {itemIdx + 1}
                    </span>
                    <p className="pt-0.5">{item.replace(/\*\*/g, "")}</p>
                  </div>
                ))}
              </div>
            </div>
          );
        }
        return (
          <p key={idx} className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
            {p.replace(/\*\*/g, "")}
          </p>
        );
      })}
    </div>
  );
}

export default function ExecutiveDashboardPage() {
  const [question, setQuestion] = useState("");
  const [answers, setAnswers] = useState<Array<{ q: string; a: string }>>([]);
  const [isAsking, setIsAsking] = useState(false);

  // Fetch briefing data
  const { data: briefingData, isLoading: isBriefingLoading } = useQuery({
    queryKey: ["executive-briefing"],
    queryFn: () => apiClient.get("/executive/briefing").then((r) => r.data),
  });

  const askMutation = useMutation({
    mutationFn: (payload: { question: string }) =>
      apiClient.post("/executive/ask", payload).then((r) => r.data),
    onSuccess: (data) => {
      setAnswers([...answers, { q: question, a: data.answer }]);
      setQuestion("");
      setIsAsking(false);
    },
    onError: () => {
      setIsAsking(false);
    },
  });

  const handleAsk = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question) return;
    setIsAsking(true);
    askMutation.mutate({ question });
  };

  const metrics = briefingData?.metrics ?? {};
  const briefingText = briefingData?.briefing ?? "Loading executive summary...";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Executive Intelligence
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Aggregated tenant analytics, automated briefings, and strategic AI
          consulting.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">        <div className="rounded-xl border bg-white p-5 shadow-sm flex items-center justify-between dark:border-dark-border dark:bg-dark-surface">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-dark-muted">
              Total Customers
            </p>
            <h3 className="text-2xl font-bold text-gray-900 mt-1 dark:text-white">
              {isBriefingLoading ? "..." : metrics.total_customers}
            </h3>
          </div>
          <div className="rounded-lg bg-blue-50 p-2.5 text-blue-600 dark:bg-dark-accent/10">
            <Users className="h-5 w-5" />
          </div>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm flex items-center justify-between dark:border-dark-border dark:bg-dark-surface">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-dark-muted">
              Average Health
            </p>              <h3 className="text-2xl font-bold text-gray-900 mt-1 dark:text-white">
              {isBriefingLoading
                ? "..."
                : `${(metrics.average_health || 0).toFixed(1)}/100`}
            </h3>
          </div>
          <div className="rounded-lg bg-green-50 p-2.5 text-green-600 dark:bg-green-500/10">
            <Heart className="h-5 w-5" />
          </div>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm flex items-center justify-between dark:border-dark-border dark:bg-dark-surface">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-dark-muted">
              Average Churn Risk
            </p>              <h3 className="text-2xl font-bold text-gray-900 mt-1 dark:text-white">
              {isBriefingLoading
                ? "..."
                : `${((metrics.average_churn || 0) * 100).toFixed(1)}%`}
            </h3>
          </div>
          <div className="rounded-lg bg-red-50 p-2.5 text-red-600 dark:bg-red-500/10">
            <ShieldAlert className="h-5 w-5" />
          </div>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm flex items-center justify-between dark:border-dark-border dark:bg-dark-surface">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-dark-muted">
              Realized Revenue
            </p>              <h3 className="text-2xl font-bold text-gray-900 mt-1 dark:text-white">
              {isBriefingLoading
                ? "..."
                : `$${(metrics.realized_revenue || 0).toLocaleString()}`}
            </h3>
          </div>
          <div className="rounded-lg bg-purple-50 p-2.5 text-purple-600 dark:bg-purple-500/10">
            <DollarSign className="h-5 w-5" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left column: AI Executive Briefing */}
        <div className="lg:col-span-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4 dark:border-dark-border dark:bg-dark-bg/60 dark:backdrop-blur-xl">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 border-b dark:border-dark-border pb-3">
            <FileText className="h-5 w-5 text-blue-600" />
            Automated Executive Briefing
          </h2>
          <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed space-y-4 whitespace-pre-wrap">
            {isBriefingLoading ? (
              <div className="space-y-3">
                <div className="h-4 w-full animate-pulse rounded bg-slate-100 dark:bg-dark-surface" />
                <div className="h-4 w-5/6 animate-pulse rounded bg-slate-100 dark:bg-dark-surface" />
                <div className="h-4 w-4/5 animate-pulse rounded bg-slate-100 dark:bg-dark-surface" />
              </div>
            ) : (
              renderBriefingText(briefingText)
            )}
          </div>
        </div>

        {/* Right column: Interactive Consulting / Q&A */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col min-h-[480px] dark:border-dark-border dark:bg-dark-bg/60 dark:backdrop-blur-xl overflow-hidden">
          {/* Panel header */}
          <div className="flex items-center gap-2 border-b border-slate-200 dark:border-dark-border px-6 py-4">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-900 dark:bg-white">
              <BarChart3 className="h-4 w-4 text-white dark:text-slate-900" />
            </div>
            <h2 className="text-base font-semibold text-gray-900 dark:text-white">
              Interactive Business Q&A
            </h2>
          </div>

          {/* Conversation area */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 max-h-[380px]">
            {answers.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full py-8 space-y-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 dark:bg-dark-surface">
                  <BarChart3 className="h-6 w-6 text-slate-400 dark:text-slate-500" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Ask a strategic question</p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Get AI-powered insights about your CRM data</p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {["Why did revenue decrease?", "Who is highest risk?", "Top upsell opportunities?"].map((q) => (
                    <button
                      key={q}
                      onClick={() => setQuestion(q)}
                      className="rounded-full border border-slate-200 dark:border-dark-border bg-slate-50 dark:bg-dark-surface px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-dark-bg transition"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {answers.map((ans, idx) => (
                  <div key={idx} className="space-y-2">
                    {/* User question */}
                    <div className="flex justify-end">
                      <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-slate-900 dark:bg-white px-4 py-2.5 text-xs text-white dark:text-slate-900">
                        {ans.q}
                      </div>
                    </div>
                    {/* AI answer */}
                    <div className="flex justify-start">
                      <div className="max-w-[90%] rounded-2xl rounded-tl-sm border border-slate-200 dark:border-dark-border bg-slate-50 dark:bg-dark-surface px-4 py-2.5 text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                        {ans.a}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Input form */}
          <div className="border-t border-slate-200 dark:border-dark-border px-4 py-3">
            <form onSubmit={handleAsk} className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Ask a strategic question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="flex-1 rounded-xl border border-slate-200 dark:border-dark-border bg-slate-50 dark:bg-dark-surface px-3 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:border-slate-400 focus:outline-none focus:bg-white dark:focus:bg-dark-bg transition"
              />
              <button
                type="submit"
                disabled={isAsking || !question}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-700 dark:hover:bg-slate-100 disabled:opacity-40 transition"
              >
                {isAsking ? (
                  <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white dark:border-slate-900 border-t-transparent" />
                ) : (
                  <Send className="h-3.5 w-3.5" />
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

