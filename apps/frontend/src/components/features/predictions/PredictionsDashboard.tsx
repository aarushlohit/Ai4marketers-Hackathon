"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  TrendingUp,
  Activity,
  Search,
  Sparkles,
  BrainCircuit,
  X,
  Star,
  ThumbsUp,
  ThumbsDown,
  Check,
  DollarSign,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  company: string | null;
  churn_probability: number | null;
  lead_score: number | null;
  health_score: number | null;
}

interface Recommendation {
  id: string;
  customer_id: string;
  type: string;
  confidence: number;
  expected_revenue: number;
  status: string;
  business_reason: string;
}

function RiskBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 70 ? "bg-red-500" : pct >= 40 ? "bg-amber-400" : "bg-green-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100 dark:bg-dark-bg">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs font-medium text-slate-700 dark:text-dark-muted">{pct}%</span>
    </div>
  );
}

export function PredictionsDashboard() {
  const [search, setSearch] = useState("");
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(
    null,
  );
  const [feedbackRating, setFeedbackRating] = useState<number>(5);
  const [feedbackText, setFeedbackText] = useState("");

  const qc = useQueryClient();

  // 1. Fetch customers
  const { data, isLoading } = useQuery({
    queryKey: ["customers-predictions", search],
    queryFn: () =>
      apiClient
        .get("/customers", {
          params: { page_size: 50, search: search || undefined },
        })
        .then((r) => r.data),
  });

  const customers: Customer[] = Array.isArray(data)
    ? data
    : (data?.customers ?? []);
  const selectedCustomer = customers.find((c) => c.id === selectedCustomerId);

  // 2. Fetch recommendations for selected customer
  const { data: recData, isLoading: isRecLoading } = useQuery({
    queryKey: ["recommendations", selectedCustomerId],
    queryFn: () => {
      if (!selectedCustomerId) return Promise.resolve([]);
      return apiClient
        .get("/recommendations", {
          params: { customer_id: selectedCustomerId },
        })
        .then((r) => r.data);
    },
    enabled: !!selectedCustomerId,
  });
  const recommendations: Recommendation[] = Array.isArray(recData)
    ? recData
    : [];

  // 3. Mutations
  const generateMutation = useMutation({
    mutationFn: (customerId: string) =>
      apiClient
        .post("/recommendations/generate", null, {
          params: { customer_id: customerId },
        })
        .then((r) => r.data),
    onSuccess: (_data, customerId) => {
      qc.invalidateQueries({
        queryKey: ["recommendations", customerId],
      });
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || err?.message || "AI Engine unavailable";
      alert(`Ask AI failed: ${msg}`);
    },
  });


  const acceptMutation = useMutation({
    mutationFn: (id: string) =>
      apiClient.post(`/recommendations/${id}/accept`).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ["recommendations", selectedCustomerId],
      });
      qc.invalidateQueries({ queryKey: ["executive-briefing"] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: string) =>
      apiClient.post(`/recommendations/${id}/reject`).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({
        queryKey: ["recommendations", selectedCustomerId],
      });
    },
  });

  const feedbackMutation = useMutation({
    mutationFn: (payload: any) =>
      apiClient.post("/feedback", payload).then((r) => r.data),
    onSuccess: () => {
      setFeedbackText("");
      alert(
        "Thank you for your feedback! The AI Decision Engine has logged it to retrain recommendations.",
      );
    },
  });

  const handleFeedbackSubmit = (recId: string) => {
    feedbackMutation.mutate({
      recommendation_id: recId,
      feedback_text: feedbackText,
      rating: feedbackRating,
      outcome_achieved: true,
    });
  };

  const highRisk = customers.filter(
    (c) => (c.churn_probability ?? 0) >= 0.7,
  ).length;

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          {
            label: "High Churn Risk",
            value: highRisk,
            icon: AlertTriangle,
            color: "text-rose-500 bg-rose-500/10",
          },
          {
            label: "Avg Lead Score",
            value: customers.length
              ? Math.round(
                  customers.reduce((s, c) => s + (c.lead_score ?? 0), 0) /
                    customers.length,
                )
              : "–",
            icon: TrendingUp,
            color: "text-blue-500 bg-blue-500/10",
          },
          {
            label: "Avg Health Score",
            value: customers.length
              ? (
                  customers.reduce((s, c) => s + (c.health_score ?? 0), 0) /
                  customers.length
                ).toFixed(1)
              : "–",
            icon: Activity,
            color: "text-emerald-500 bg-emerald-500/10",
          },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500 dark:text-dark-muted">{label}</p>
              <span className={`rounded-xl p-2 ${color}`}>
                <Icon className="h-4 w-4" />
              </span>
            </div>
            <p className="mt-2 text-3xl font-bold text-slate-800 dark:text-white">{value}</p>
          </div>
        ))}
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-dark-muted" />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search customers…"
          className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 pl-9 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-bg/50 dark:text-white dark:placeholder-dark-muted"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Table list */}
        <div className="lg:col-span-2 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
          <table className="min-w-full divide-y divide-slate-200 dark:divide-dark-border text-slate-600 dark:text-dark-muted">
            <thead className="bg-slate-50 dark:bg-dark-bg/50 text-slate-500">
              <tr>
                {["Customer", "Churn Risk", "Health Score", "Action"].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-dark-border">
              {isLoading
                ? Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i}>
                      {[...Array(4)].map((_, j) => (
                        <td key={j} className="px-6 py-4">
                          <div className="h-4 animate-pulse rounded bg-slate-100 dark:bg-dark-surface" />
                        </td>
                      ))}
                    </tr>
                  ))
                : customers.map((c) => (
                    <tr
                      key={c.id}
                      className="hover:bg-slate-50 dark:hover:bg-dark-bg/30 cursor-pointer"
                      onClick={() => setSelectedCustomerId(c.id)}
                    >
                      <td className="px-6 py-4 text-sm font-semibold text-slate-800 dark:text-white">
                        {c.first_name} {c.last_name}
                        {c.company && (
                          <span className="ml-2 text-xs text-slate-400 dark:text-dark-muted">
                            {c.company}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {c.churn_probability != null ? (
                          <RiskBar value={c.churn_probability} />
                        ) : (
                          <span className="text-xs text-slate-400 dark:text-dark-muted">–</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-700 dark:text-dark-muted">
                        {c.health_score != null
                          ? c.health_score.toFixed(1)
                          : "–"}
                      </td>
                      <td className="px-6 py-4 text-xs font-semibold text-blue-600 dark:text-blue-400 flex items-center gap-1">
                        <BrainCircuit className="h-4 w-4" /> Recommend
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
        </div>

        {/* Right drawer: Intelligence Center */}
        {selectedCustomer && (
          <div className="lg:col-span-1 rounded-2xl border border-blue-200 bg-white p-6 shadow-sm space-y-4 h-fit dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
            <div className="flex items-center justify-between border-b pb-3 dark:border-dark-border">
              <div>
                <h3 className="font-bold text-slate-800 dark:text-white">
                  {selectedCustomer.first_name} {selectedCustomer.last_name}
                </h3>
                <p className="text-xs text-slate-500 dark:text-dark-muted">
                  {selectedCustomer.company}
                </p>
              </div>
              <button
                onClick={() => setSelectedCustomerId(null)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-100 dark:bg-dark-bg/30 dark:border-dark-border">
                <span className="font-semibold text-slate-700 dark:text-slate-300">
                  Health: {selectedCustomer.health_score?.toFixed(1) ?? "N/A"}
                </span>
                <span className="font-semibold text-rose-500 dark:text-rose-400">
                  Churn Risk:{" "}
                  {selectedCustomer.churn_probability != null
                    ? `${(selectedCustomer.churn_probability * 100).toFixed(0)}%`
                    : "N/A"}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-slate-800 dark:text-white flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  Prescriptive AI Actions
                </h4>
                <button
                  onClick={() => generateMutation.mutate(selectedCustomer.id)}
                  disabled={generateMutation.isPending}
                  className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {generateMutation.isPending ? "Analyzing..." : "Ask AI"}
                </button>
              </div>

              {isRecLoading ? (
                <div className="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-dark-surface" />
              ) : recommendations.length === 0 ? (
                <p className="text-xs text-slate-400 dark:text-dark-muted text-center py-4">
                  No active recommendations. Click &quot;Ask AI&quot; to
                  generate real-time advice.
                </p>
              ) : (
                <div className="space-y-4">
                  {recommendations.map((rec) => (
                    <div
                      key={rec.id}
                      className="rounded-xl border border-slate-100 bg-slate-50 p-4 space-y-3 dark:bg-dark-bg/30 dark:border-dark-border"
                    >
                      <div className="flex justify-between items-start">
                        <span className="inline-flex rounded-full bg-blue-50 dark:bg-blue-500/10 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:text-blue-400">
                          {rec.type}
                        </span>
                        <span className="text-xs text-slate-500 dark:text-dark-muted font-medium">
                          Confidence: {(rec.confidence * 100).toFixed(0)}%
                        </span>
                      </div>

                      <div className="flex items-center gap-1 text-sm font-semibold text-emerald-600 dark:text-emerald-500">
                        <DollarSign className="h-4 w-4" />
                        Expected ROI: ${rec.expected_revenue.toLocaleString()}
                      </div>

                      <p className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
                        {rec.business_reason}
                      </p>

                      {rec.status === "Pending" ? (
                        <div className="flex gap-2 pt-2">
                          <button
                            onClick={() => acceptMutation.mutate(rec.id)}
                            className="flex-1 flex items-center justify-center gap-1 rounded-lg bg-emerald-600 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
                          >
                            <ThumbsUp className="h-3 w-3" /> Accept
                          </button>
                          <button
                            onClick={() => rejectMutation.mutate(rec.id)}
                            className="flex-1 flex items-center justify-center gap-1 rounded-lg bg-rose-600 py-1.5 text-xs font-semibold text-white hover:bg-rose-700"
                          >
                            <ThumbsDown className="h-3 w-3" /> Reject
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 pt-2 bg-slate-100/50 p-2 rounded-lg dark:bg-dark-bg/50 dark:text-dark-muted">
                          <Check className="h-4 w-4 text-emerald-600" />
                          Marked as:{" "}
                          <span className="capitalize">{rec.status}</span>
                        </div>
                      )}

                      {/* Feedback Loop */}
                      <div className="border-t border-slate-200 dark:border-dark-border pt-3 space-y-2">
                        <p className="text-[10px] font-semibold text-slate-400 dark:text-dark-muted uppercase">
                          Rate AI Decision Quality
                        </p>
                        <div className="flex gap-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <Star
                              key={star}
                              onClick={() => setFeedbackRating(star)}
                              className={`h-4 w-4 cursor-pointer ${star <= feedbackRating ? "fill-amber-400 text-amber-400 animate-pulse" : "text-slate-300 dark:text-dark-muted"}`}
                            />
                          ))}
                        </div>
                        <textarea
                          placeholder="Log salesperson feedback..."
                          rows={2}
                          value={feedbackText}
                          onChange={(e) => setFeedbackText(e.target.value)}
                          className="w-full rounded-lg border border-slate-200 p-1.5 text-[11px] focus:outline-none dark:border-dark-border dark:bg-dark-bg/30 dark:text-white"
                        />
                        <button
                          onClick={() => handleFeedbackSubmit(rec.id)}
                          className="w-full bg-slate-800 text-white rounded-lg py-1 text-[10px] font-semibold hover:bg-slate-900 dark:bg-blue-600 dark:hover:bg-blue-700"
                        >
                          Submit to Feedback Loop
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
