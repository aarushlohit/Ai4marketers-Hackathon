"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, TrendingUp, Users } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { formatCurrency, formatPercent } from "@/lib/utils";

interface DashboardData {
  total_customers: number;
  active_customers: number;
  at_risk_customers: number;
  churn_rate: number;
  avg_health_score: number;
  time_range: string;
}

function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  color = "blue",
}: {
  title: string;
  value: string | number;
  description?: string;
  icon: React.ElementType;
  color?: "blue" | "green" | "red" | "amber";
}) {
  const colorMap = {
    blue: "bg-blue-50 text-blue-700",
    green: "bg-green-50 text-green-700",
    red: "bg-red-50 text-red-700",
    amber: "bg-amber-50 text-amber-700",
  };

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <span className={`rounded-lg p-2 ${colorMap[color]}`}>
          <Icon className="h-5 w-5" />
        </span>
      </div>
      <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
      {description && (
        <p className="mt-1 text-xs text-gray-500">{description}</p>
      )}
    </div>
  );
}

export function DashboardMetrics() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ["dashboard-metrics"],
    queryFn: () =>
      apiClient.get("/analytics/dashboard?time_range=30d").then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-32 animate-pulse rounded-xl bg-gray-100" />
        ))}
      </div>
    );
  }

  if (error || !data) {
    return (
      <p className="text-sm text-red-500">Failed to load dashboard metrics.</p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        title="Total Customers"
        value={data.total_customers.toLocaleString()}
        description={`${data.active_customers.toLocaleString()} active`}
        icon={Users}
        color="blue"
      />
      <MetricCard
        title="At-Risk Customers"
        value={data.at_risk_customers.toLocaleString()}
        description="Churn probability ≥ 70%"
        icon={AlertTriangle}
        color="red"
      />
      <MetricCard
        title="Churn Rate"
        value={formatPercent(data.churn_rate)}
        description="Last 30 days"
        icon={TrendingUp}
        color="amber"
      />
      <MetricCard
        title="Avg Health Score"
        value={data.avg_health_score.toFixed(1)}
        description="Out of 100"
        icon={TrendingUp}
        color="green"
      />
    </div>
  );
}
