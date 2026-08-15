"use client";

import { memo, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
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
    <div className="grid h-[250px] min-w-0 w-full grid-cols-5 items-end gap-3 px-2 pb-1 pt-4">
      {stages.map((entry) => {
        const maxCount = Math.max(...stages.map((stage) => stage.count), 1);
        const height = entry.count === 0 ? 4 : Math.max((entry.count / maxCount) * 190, 12);
        return (
          <div key={entry.stage} className="flex h-full min-w-0 flex-col items-center justify-end gap-2" title={`${entry.stage}: ${entry.count} accounts`}>
            <span className="text-xs font-semibold text-slate-500">{entry.count}</span>
            <div className="w-full max-w-12 rounded-t-lg transition-all" style={{ height, backgroundColor: entry.color }} />
            <span className="w-full truncate text-center text-[11px] text-slate-500">{entry.stage}</span>
          </div>
        );
      })}
    </div>
  );
});
