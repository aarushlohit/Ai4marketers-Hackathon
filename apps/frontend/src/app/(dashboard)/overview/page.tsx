"use client";

import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  TrendingUp,
  DollarSign,
  Flame,
  Sparkles,
} from "lucide-react";
import { memo, Suspense, lazy } from "react";
import { apiClient } from "@/lib/api/client";
import { formatCurrency } from "@/lib/utils";

const SalesPipelineChart = lazy(() =>
  import("@/components/features/analytics/SalesPipelineChart").then((m) => ({
    default: m.SalesPipelineChart,
  })),
);

interface DashboardData {
  total_customers: number;
  active_customers: number;
  at_risk_customers: number;
  churn_rate: number;
  avg_health_score: number;
  revenue_forecast: number;
  hot_leads: number;
  time_range: string;
}

const MetricCard = memo(function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  color = "blue",
}: {
  title: string;
  value: string;
  description?: string;
  icon: React.ComponentType<{ className?: string }>;
  color?: string;
}) {
  const colorMap: Record<string, string> = {
    blue: "bg-blue-50 text-blue-600 border-blue-100 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20",
    green: "bg-emerald-50 text-emerald-600 border-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20",
    red: "bg-rose-50 text-rose-600 border-rose-100 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/20",
    amber: "bg-amber-50 text-amber-600 border-amber-100 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20",
    purple: "bg-purple-50 text-purple-600 border-purple-100 dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/20",
    orange: "bg-orange-50 text-orange-600 border-orange-100 dark:bg-orange-500/10 dark:text-orange-400 dark:border-orange-500/20",
  };

  return (
    <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500 dark:text-dark-muted">
          {title}
        </p>
        <span className={`rounded-2xl border p-2.5 ${colorMap[color]}`}>
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <p className="mt-4 text-3xl font-bold tracking-tight text-slate-800 dark:text-white">
        {value}
      </p>
      {description && (
        <p className="mt-2 text-sm font-medium text-slate-400 dark:text-dark-muted">
          {description}
        </p>
      )}
    </div>
  );
});

const RECOMMENDATIONS = [
  {
    title: "Follow-up required",
    desc: "Acme Corp showed high engagement on the pricing page. Probability of close: 89%",
    action: "Schedule Call",
    color: "text-emerald-600 dark:text-emerald-400",
    bg: "bg-emerald-50 dark:bg-emerald-950/10",
  },
  {
    title: "Churn Risk Detected",
    desc: "TechGlobal's activity dropped by 45% this week. Health score is declining.",
    action: "Send Offer",
    color: "text-rose-600 dark:text-rose-400",
    bg: "bg-rose-50 dark:bg-rose-950/10",
  },
  {
    title: "Upsell Opportunity",
    desc: "CloudSync has maxed out their current tier limits. Expected upgrade revenue: $12k.",
    action: "Send Proposal",
    color: "text-blue-600 dark:text-blue-400",
    bg: "bg-blue-50 dark:bg-blue-950/10",
  },
] as const;

const AIRecommendations = memo(function AIRecommendations() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
      <div className="mb-6 flex items-center gap-3">
        <div className="rounded-2xl bg-blue-50 p-2.5 text-blue-600 dark:bg-dark-accent/10">
          <Sparkles className="h-5 w-5" />
        </div>
        <h2 className="text-xl font-bold text-slate-800 dark:text-white">
          Next Best Actions
        </h2>
      </div>
      <div className="space-y-4">
        {RECOMMENDATIONS.map((rec) => (
          <div
            key={rec.title}
            className={`flex flex-col gap-4 rounded-2xl border border-slate-100 ${rec.bg} p-5 transition-colors hover:border-slate-200 sm:flex-row sm:items-center sm:justify-between dark:border-dark-border dark:hover:border-dark-border`}
          >
            <div>
              <p className={`text-sm font-bold ${rec.color}`}>{rec.title}</p>
              <p className="mt-1 text-sm font-medium text-slate-600 dark:text-slate-300">
                {rec.desc}
              </p>
            </div>
            <button
              type="button"
              className="shrink-0 rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:shadow dark:bg-dark-bg dark:text-white dark:border dark:border-dark-border dark:hover:bg-dark-surface"
            >
              {rec.action}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
});

function DashboardMetrics() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ["dashboard-metrics"],
    queryFn: () =>
      apiClient.get("/analytics/dashboard?time_range=30d").then((r) => r.data),
    staleTime: 60_000,
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-36 animate-pulse rounded-3xl bg-white dark:bg-dark-surface shadow-sm"
          />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-rose-100 bg-rose-50 p-6 text-center shadow-sm dark:border-rose-950/20 dark:bg-rose-950/20">
        <AlertTriangle className="mx-auto mb-2 h-8 w-8 text-rose-500" />
        <p className="font-semibold text-rose-700 dark:text-rose-400">
          Failed to load dashboard metrics.
        </p>
        <p className="mt-1 text-sm text-rose-600 dark:text-rose-400/80">
          Please ensure the backend API is running and accessible.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Revenue Forecast (Q3)"
          value={formatCurrency(data.revenue_forecast)}
          description="Predicted 15% increase"
          icon={DollarSign}
          color="green"
        />
        <MetricCard
          title="Hot Leads"
          value={data.hot_leads.toLocaleString()}
          description="Ready for sales contact"
          icon={Flame}
          color="orange"
        />
        <MetricCard
          title="High Risk Customers"
          value={data.at_risk_customers.toLocaleString()}
          description="Churn probability ≥ 70%"
          icon={AlertTriangle}
          color="red"
        />
        <MetricCard
          title="Avg Health Score"
          value={data.avg_health_score.toFixed(1)}
          description="Across all accounts"
          icon={TrendingUp}
          color="blue"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <AIRecommendations />

        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-800 dark:text-white">
              Sales Pipeline
            </h2>
            <span className="text-xs font-semibold text-slate-400 dark:text-dark-muted">
              By account stage
            </span>
          </div>
          <Suspense
            fallback={
              <div className="h-[250px] animate-pulse rounded-2xl bg-slate-100 dark:bg-dark-bg" />
            }
          >
            <SalesPipelineChart />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

import { CreatedBySection } from "@/components/CreatedBySection";

export default function OverviewPage() {
  return (
    <div className="min-h-screen p-8 font-sans md:p-12 space-y-10">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Executive Dashboard
        </h1>
        <p className="mt-3 text-lg font-medium text-slate-500 dark:text-dark-muted">
          AI-powered CRM intelligence and next best actions powered by Miracle
          Birds.
        </p>
      </div>
      <DashboardMetrics />
      <CreatedBySection />
    </div>
  );
}
