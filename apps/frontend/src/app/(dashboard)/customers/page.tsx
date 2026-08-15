"use client";

import { useState } from "react";
import { Search, ChevronRight, Activity, AlertCircle, RefreshCw, ChevronDown } from "lucide-react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth.store";


interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  company: string | null;
  status: string;
  churn_probability: number | null;
  health_score: number | null;
}

interface Connection {
  id: string;
  crm_type: string;
  status: string;
}

export default function CustomersPage() {
  const [search, setSearch] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { user, accessToken } = useAuthStore();


  // Fetch real customers from the backend API
  const { data: customerData, isLoading: isLoadingCustomers, refetch: refetchCustomers } = useQuery<{
    customers: Customer[];
    total: number;
  }>({
    queryKey: ["customers", search],
    queryFn: () =>
      apiClient
        .get("/customers", { params: { search: search || undefined } })
        .then((r) => r.data),
  });

  // Fetch active CRM connections to generate the sync buttons
  const { data: connectionsData, isLoading: isLoadingConnections } = useQuery<{
    connections: Connection[];
  }>({
    queryKey: ["crm-connections", accessToken],
    queryFn: () => apiClient.get("/integrations/connections").then((r) => r.data),
    staleTime: 0,
    gcTime: 0,
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    enabled: !!accessToken,
  });


  const connections = connectionsData?.connections ?? [];

  // Sync Mutation
  const syncMutation = useMutation({
    mutationFn: (connectionId: string) =>
      apiClient.post(`/integrations/sync/${connectionId}/start`),
    onSuccess: () => {
      alert("CRM synchronization started! Refreshing customer list...");
      refetchCustomers();
    },
    onError: (err: any) => {
      alert("CRM sync failed to start: " + err.message);
    },
  });

  const handleSync = (connectionId: string) => {
    setDropdownOpen(false);
    syncMutation.mutate(connectionId);
  };

  const getRiskLabel = (prob: number | null) => {
    if (prob === null) return "Low";
    const pct = prob * 100;
    if (pct >= 70) return "High";
    if (pct >= 40) return "Medium";
    return "Low";
  };

  const renderSyncButton = () => {
    if (isLoadingConnections) {
      return (
        <button disabled className="flex items-center gap-2 rounded-lg bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-400 dark:bg-dark-surface dark:text-dark-muted">
          <RefreshCw className="h-4 w-4 animate-spin" /> Loading Connections...
        </button>
      );
    }

    if (connections.length === 0) {
      return (
        <a
          href="/marketplace"
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Connect CRM to Sync
        </a>
      );
    }

    if (connections.length === 1) {
      const conn = connections[0];
      const displayName = conn.crm_type.charAt(0).toUpperCase() + conn.crm_type.slice(1);
      return (
        <button
          onClick={() => handleSync(conn.id)}
          disabled={syncMutation.isPending}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
        >
          {syncMutation.isPending ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          Sync with {displayName}
        </button>
      );
    }

    // Multiple connections -> show dropdown
    return (
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          <RefreshCw className="h-4 w-4" />
          Sync CRM
          <ChevronDown className="h-4 w-4" />
        </button>
        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-48 rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none dark:bg-dark-surface z-50">
            <div className="py-1">
              {connections.map((conn) => {
                const displayName = conn.crm_type.charAt(0).toUpperCase() + conn.crm_type.slice(1);
                return (
                  <button
                    key={conn.id}
                    onClick={() => handleSync(conn.id)}
                    className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-dark-bg"
                  >
                    Sync with {displayName}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  const customers = customerData?.customers ?? [];

  return (
    <div className="min-h-full space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Customers
          </h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-dark-muted">
            Manage your CRM leads, organizations, and sync statuses.
          </p>
        </div>
        {renderSyncButton()}
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400 dark:text-dark-muted" />
          <input
            type="text"
            placeholder="Search customers..."
            className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-slate-900 placeholder-slate-400 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-bg/50 dark:text-white dark:placeholder-dark-muted"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
        <table className="w-full text-left text-sm text-slate-600 dark:text-dark-muted">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 dark:bg-dark-bg/50">
            <tr>
              <th className="px-6 py-4 font-semibold">Organization</th>
              <th className="px-6 py-4 font-semibold">Health Score</th>
              <th className="px-6 py-4 font-semibold">Churn Risk</th>
              <th className="px-6 py-4 font-semibold">Status</th>
              <th className="px-6 py-4 font-semibold">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-dark-border">
            {isLoadingCustomers ? (
              <tr>
                <td colSpan={5} className="px-6 py-10 text-center text-slate-400 dark:text-dark-muted">
                  <RefreshCw className="mx-auto h-6 w-6 animate-spin mb-2" />
                  Loading customers...
                </td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-10 text-center text-slate-400 dark:text-dark-muted">
                  No customers found. Trigger a CRM sync above to load your data.
                </td>
              </tr>
            ) : (
              customers.map((c) => {
                const risk = getRiskLabel(c.churn_probability);
                const health = c.health_score ?? 0;
                return (
                  <tr
                    key={c.id}
                    className="transition-colors hover:bg-slate-50 dark:hover:bg-dark-surface/50"
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900 dark:text-white">
                        {c.company || `${c.first_name} ${c.last_name}`}
                      </div>
                      <div className="text-slate-500 dark:text-slate-400">
                        {c.email || "No email"}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <Activity
                          className={`h-4 w-4 ${health > 80 ? "text-emerald-500" : health > 50 ? "text-amber-500" : "text-rose-500"}`}
                        />
                        <span className="text-slate-900 dark:text-white font-medium">
                          {health.toFixed(0)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          risk === "High"
                            ? "bg-rose-50 text-rose-600 border border-rose-100 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/20"
                            : risk === "Medium"
                              ? "bg-amber-50 text-amber-600 border border-amber-100 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20"
                              : "bg-emerald-50 text-emerald-600 border border-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20"
                        }`}
                      >
                        {risk === "High" && <AlertCircle className="h-3 w-3" />}
                        {risk}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium capitalize">{c.status}</span>
                    </td>
                    <td className="px-6 py-4">
                      <a
                        href={`/customers/${c.id}`}
                        className="inline-flex items-center font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                      >
                        View 360 <ChevronRight className="ml-1 h-4 w-4" />
                      </a>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
