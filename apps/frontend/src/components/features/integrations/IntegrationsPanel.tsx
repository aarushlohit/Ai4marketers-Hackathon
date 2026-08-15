"use client";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, XCircle, RefreshCw, Plug, Trash2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";

import { CrmLogo, CRMType } from "@/components/CrmLogos";

const CRM_PLATFORMS: { id: CRMType; name: string }[] = [
  { id: "salesforce", name: "Salesforce" },
  { id: "zoho", name: "Zoho CRM" },
  { id: "hubspot", name: "HubSpot" },
  { id: "dynamics", name: "Dynamics 365" },
  { id: "pipedrive", name: "Pipedrive" },
];

interface Connection {
  id: string;
  crm_type: CRMType;
  status: "active" | "inactive" | "error";
  last_sync: string | null;
  instance_url: string | null;
}

export function IntegrationsPanel() {
  const qc = useQueryClient();
  const [syncing, setSyncing] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("status") === "connected") {
      const crm = params.get("integration");
      setNotice(`${crm ? crm[0].toUpperCase() + crm.slice(1) : "CRM"} connected successfully.`);
      qc.invalidateQueries({ queryKey: ["crm-connections"] });
      window.history.replaceState({}, "", "/integrations");
    }
  }, [qc]);

  const { data, isLoading } = useQuery({
    queryKey: ["crm-connections"],
    queryFn: () =>
      apiClient.get("/integrations/connections").then((r) => r.data),
  });

  const connections: Connection[] = data?.connections ?? [];
  const connectedIds = new Set(connections.map((c) => c.crm_type));

  const connectMutation = useMutation({
    mutationFn: (crm: CRMType) =>
      apiClient.get(`/integrations/${crm}/authorize`).then((r) => r.data),
    onSuccess: (data) => {
      alert("Success Response: " + JSON.stringify(data));
      if (data.authorization_url) {
        window.location.href = data.authorization_url;
      }
    },
    onError: (err) => {
      console.error("Connection error:", err);
      const errorDetail = (err as any).response?.data?.detail || (err as any).message;
      alert("Failed to connect: " + errorDetail);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      apiClient.delete(`/integrations/connections/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["crm-connections"] }),
  });

  const syncMutation = useMutation({
    mutationFn: (id: string) => {
      setSyncing(id);
      return apiClient
        .post(`/integrations/sync/${id}/start?sync_type=incremental`)
        .then((r) => r.data);
    },
    onSettled: () => setSyncing(null),
  });

  return (
    <div className="space-y-6">
      {notice && (
        <div className="flex items-center justify-between rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 dark:border-green-500/30 dark:bg-green-500/10 dark:text-green-300">
          <span className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4" />{notice}</span>
          <button onClick={() => setNotice(null)} className="text-green-700 dark:text-green-300" aria-label="Dismiss notification">Dismiss</button>
        </div>
      )}
      {/* Connected */}
      {connections.length > 0 && (
        <div>
          <h2 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
            Connected CRMs
          </h2>
          <div className="space-y-3">
            {connections.map((conn) => {
              const platform = CRM_PLATFORMS.find(
                (p) => p.id === conn.crm_type,
              );
              return (
                <div
                  key={conn.id}
                  className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-dark-border dark:bg-dark-surface"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-50 dark:bg-dark-bg p-1.5 border border-slate-100 dark:border-dark-border">
                      <CrmLogo type={conn.crm_type} className="h-6 w-6 shrink-0" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {platform?.name}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-dark-muted">
                        Last sync:{" "}
                        {conn.last_sync
                          ? new Date(conn.last_sync).toLocaleString()
                          : "Never"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                        conn.status === "active"
                          ? "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-300"
                          : "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-300"
                      }`}
                    >
                      {conn.status === "active" ? (
                        <CheckCircle2 className="h-3 w-3" />
                      ) : (
                        <XCircle className="h-3 w-3" />
                      )}
                      {conn.status === "active" ? "Connected" : conn.status}
                    </span>
                    <button
                      onClick={() => syncMutation.mutate(conn.id)}
                      disabled={syncing === conn.id}
                      className="rounded-lg border border-slate-200 p-1.5 hover:bg-gray-50 dark:border-dark-border dark:hover:bg-dark-bg disabled:opacity-40"
                      title="Sync now"
                    >
                      <RefreshCw
                        className={`h-4 w-4 text-gray-500 ${syncing === conn.id ? "animate-spin" : ""}`}
                      />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(conn.id)}
                      className="rounded-lg border border-slate-200 p-1.5 hover:bg-red-50 dark:border-dark-border dark:hover:bg-red-500/10"
                      title="Disconnect"
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Available to connect */}
      <div>
          <h2 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">
          Available Integrations
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {CRM_PLATFORMS.filter((p) => !connectedIds.has(p.id)).map(
            (platform) => (
              <div
                key={platform.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-dark-border dark:bg-dark-surface"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-50 dark:bg-dark-bg p-1.5 border border-slate-100 dark:border-dark-border">
                    <CrmLogo type={platform.id} className="h-6 w-6 shrink-0" />
                  </div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {platform.name}
                  </p>
                </div>
                <button
                  onClick={() => connectMutation.mutate(platform.id)}
                  disabled={connectMutation.isPending}
                  className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  <Plug className="h-3 w-3" />
                  Connect
                </button>
              </div>
            ),
          )}
          {connectedIds.size === CRM_PLATFORMS.length && (
              <p className="col-span-full text-sm text-gray-400 dark:text-dark-muted">
              All CRM platforms are connected.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
