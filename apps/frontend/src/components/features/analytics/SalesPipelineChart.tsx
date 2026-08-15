"use client";

import { memo, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { apiClient } from "@/lib/api/client";

interface PipelineStage {
  stage: string;
  count: number;
  color: string;
}

interface PipelineData {
  stages: PipelineStage[];
  total: number;
}

function PipelineSkeleton() {
  return (
    <div className="flex h-[250px] items-center justify-center">
      <div className="h-full w-full animate-pulse rounded-2xl bg-slate-100 dark:bg-dark-bg" />
    </div>
  );
}

function PipelineEmpty() {
  return (
    <div className="flex h-[250px] flex-col items-center justify-center gap-2 text-slate-400 dark:text-dark-muted">
      <p className="text-sm font-medium">No pipeline data yet</p>
      <p className="text-xs">Add customers to see stage distribution</p>
    </div>
  );
}

export const SalesPipelineChart = memo(function SalesPipelineChart() {
  const { data, isLoading, error } = useQuery<PipelineData>({
    queryKey: ["pipeline-stages"],
    queryFn: () => apiClient.get("/analytics/pipeline").then((r) => r.data),
    staleTime: 60_000,
    retry: 1,
  });

  const stages = useMemo(() => data?.stages ?? [], [data?.stages]);
  const hasData = stages.some((s) => s.count > 0);

  if (isLoading) return <PipelineSkeleton />;

  if (error || !data) {
    return (
      <div className="flex h-[250px] items-center justify-center text-sm text-rose-500">
        Failed to load pipeline data
      </div>
    );
  }

  if (!hasData) return <PipelineEmpty />;

  return (
    <div className="h-[250px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={stages}
          margin={{ top: 8, right: 8, left: -8, bottom: 0 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#e2e8f0"
            vertical={false}
          />
          <XAxis
            dataKey="stage"
            tick={{ fontSize: 12, fill: "#64748b" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#64748b" }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip
            cursor={{ fill: "rgba(148, 163, 184, 0.12)" }}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid #e2e8f0",
              fontSize: 13,
            }}
            formatter={(value: number) => [value, "Accounts"]}
          />
          <Bar dataKey="count" radius={[8, 8, 0, 0]} maxBarSize={48}>
            {stages.map((entry) => (
              <Cell key={entry.stage} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
});
