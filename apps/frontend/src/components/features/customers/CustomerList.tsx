"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { getInitials, formatPercent } from "@/lib/utils";

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  company: string | null;
  status: string;
  churn_probability: number | null;
  health_score: number | null;
  lead_score: number | null;
}

interface CustomerListResponse {
  customers: Customer[];
  total: number;
  page: number;
  page_size: number;
}

function RiskBadge({ probability }: { probability: number | null }) {
  if (probability == null)
    return <span className="text-gray-400 text-xs">–</span>;
  const pct = probability * 100;
  if (pct >= 70)
    return (
      <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
        High
      </span>
    );
  if (pct >= 40)
    return (
      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
        Medium
      </span>
    );
  return (
    <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
      Low
    </span>
  );
}

export function CustomerList() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery<CustomerListResponse>({
    queryKey: ["customers", page, search],
    queryFn: () =>
      apiClient
        .get("/customers", {
          params: { page, page_size: 20, search: search || undefined },
        })
        .then((r) => r.data),
    placeholderData: (prev) => prev,
  });

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder="Search customers…"
          className="w-full max-w-sm rounded-lg border border-gray-300 py-2 pl-9 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {[
                "Customer",
                "Company",
                "Status",
                "Churn Risk",
                "Health Score",
              ].map((h) => (
                <th
                  key={h}
                  className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {isLoading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 5 }).map((_, j) => (
                      <td key={j} className="px-6 py-4">
                        <div className="h-4 animate-pulse rounded bg-gray-100" />
                      </td>
                    ))}
                  </tr>
                ))
              : data?.customers.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50 cursor-pointer">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700">
                          {getInitials(`${c.first_name} ${c.last_name}`)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {c.first_name} {c.last_name}
                          </p>
                          <p className="text-xs text-gray-500">{c.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {c.company ?? "–"}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                          c.status === "active"
                            ? "bg-green-100 text-green-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <RiskBadge probability={c.churn_probability} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {c.health_score != null ? c.health_score.toFixed(1) : "–"}
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>

        {/* Pagination */}
        {data && data.total > data.page_size && (
          <div className="flex items-center justify-between border-t px-6 py-3">
            <p className="text-xs text-gray-500">
              Showing {(page - 1) * data.page_size + 1}–
              {Math.min(page * data.page_size, data.total)} of {data.total}
            </p>
            <div className="flex gap-2">
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                className="rounded px-3 py-1 text-xs border hover:bg-gray-50 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                disabled={page * data.page_size >= data.total}
                onClick={() => setPage((p) => p + 1)}
                className="rounded px-3 py-1 text-xs border hover:bg-gray-50 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
