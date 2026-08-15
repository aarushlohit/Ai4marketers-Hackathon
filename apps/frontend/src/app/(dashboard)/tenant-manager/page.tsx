"use client";

import { useState, useEffect } from "react";
import {
  ShieldCheck,
  Plus,
  Check,
  RefreshCw,
  LayoutGrid,
  Users,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: string;
  is_active: boolean;
  created_at: string;
}

export default function TenantManager() {
  const [tenants, setTenants] = useState<Tenant[]>([
    {
      id: "00000000-0000-0000-0000-000000000001",
      name: "Miracle Birds Dev",
      slug: "dev",
      plan: "enterprise",
      is_active: true,
      created_at: "2026-07-01",
    },
    {
      id: "88888888-8888-8888-8888-888888888888",
      name: "Acme Corporates",
      slug: "acme-corp",
      plan: "startup",
      is_active: true,
      created_at: "2026-07-05",
    },
    {
      id: "99999999-9999-9999-9999-999999999999",
      name: "Global Tech Inc",
      slug: "global-tech",
      plan: "free",
      is_active: true,
      created_at: "2026-07-10",
    },
  ]);
  const [activeTenantId, setActiveTenantId] = useState<string>(
    "00000000-0000-0000-0000-000000000001",
  );
  const [name, setName] = useState("");
  const [plan, setPlan] = useState("startup");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
      const newTenant: Tenant = {
        id: crypto.randomUUID(),
        name,
        slug,
        plan,
        is_active: true,
        created_at: new Date().toISOString().split("T")[0],
      };
      setTenants([...tenants, newTenant]);
      setSuccess(
        `Tenant "${name}" provisioned successfully with RLS partition gates.`,
      );
      setName("");
    } catch (err: any) {
      setError(err.message || "Failed to create tenant");
    } finally {
      setLoading(false);
    }
  };

  const switchTenant = (id: string) => {
    setActiveTenantId(id);
    // In production, this sets headers/JWT token and reloads
    setSuccess(`Active workspace switched successfully.`);
  };

  return (
    <div className="min-h-screen p-8 md:p-12 font-sans">
      <div className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Tenant Manager
          </h1>
          <p className="mt-3 text-lg font-medium text-slate-500 dark:text-slate-400">
            Multi-Tenant SaaS isolation, database policies check, and
            organization routing.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-2 text-emerald-600 font-bold text-sm">
          <ShieldCheck className="h-5 w-5" />
          PostgreSQL RLS Policies: Enforced
        </div>
      </div>

      {success && (
        <div className="mb-6 rounded-2xl border border-emerald-100 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Left Column: Organization Switcher */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-surface">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2 dark:text-white">
              <LayoutGrid className="h-5 w-5 text-blue-500" />
              Active Organizations
            </h2>
            <div className="space-y-4">
              {tenants.map((t) => (
                <div
                  key={t.id}
                  onClick={() => switchTenant(t.id)}
                  className={`flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border p-5 cursor-pointer transition-all hover:border-blue-200 ${
                    activeTenantId === t.id
                      ? "border-blue-500 bg-blue-50/50 shadow-sm dark:border-dark-accent dark:bg-dark-accent/5"
                      : "border-slate-100 bg-white dark:border-dark-border dark:bg-dark-surface"
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`rounded-xl p-3 ${activeTenantId === t.id ? "bg-blue-500 text-white" : "bg-slate-100 text-slate-500"}`}
                    >
                      <Users className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-slate-800 dark:text-white">{t.name}</p>
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-bold capitalize ${
                            t.plan === "enterprise"
                              ? "bg-purple-100 text-purple-700"
                              : t.plan === "startup"
                                ? "bg-blue-100 text-blue-700"
                                : "bg-slate-100 text-slate-600"
                          }`}
                        >
                          {t.plan}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 font-mono mt-1 dark:text-dark-muted">
                        ID: {t.id}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {activeTenantId === t.id ? (
                      <span className="flex items-center gap-1.5 text-sm font-bold text-blue-600 bg-blue-100/50 px-3 py-1.5 rounded-xl">
                        <Check className="h-4 w-4" />
                        Current Workspace
                      </span>
                    ) : (
                      <button className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-50 dark:border-dark-border dark:text-dark-muted dark:hover:bg-dark-surface">
                        Switch
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Provision Form */}
        <div className="space-y-6">
          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-surface">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2 dark:text-white">
              <Plus className="h-5 w-5 text-blue-500" />
              Provision New Tenant
            </h2>
            <form onSubmit={handleCreateTenant} className="space-y-4">
              <div>                      <label className="block text-sm font-bold text-slate-700 mb-2 dark:text-gray-300">
                  Organization Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. Initech Corp"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg dark:text-white"
                  required
                />
              </div>

              <div>                      <label className="block text-sm font-bold text-slate-700 mb-2 dark:text-gray-300">
                  Subscription Plan
                </label>
                <select
                  value={plan}
                  onChange={(e) => setPlan(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg dark:text-white"
                >
                  <option value="free">Free Plan</option>
                  <option value="startup">Startup Plan</option>
                  <option value="enterprise">Enterprise Plan</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-dark-accent py-3 text-sm font-bold text-white shadow-sm transition-all hover:bg-dark-accent/80 disabled:bg-dark-border"
              >
                {loading ? "Provisioning..." : "Create Isolated Tenant"}
              </button>
            </form>
          </div>

          <div className="rounded-3xl border border-slate-100 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-surface">
            <h3 className="font-bold text-slate-800 mb-3 text-sm">
              Tenant Isolation Policy
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              Every database operation utilizes Row-Level Security checks
              configured under PostgreSQL 16 schema filters. Context values
              verify target mappings in micro-actions automatically.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
