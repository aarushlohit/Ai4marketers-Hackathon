"use client";

import { useState, useEffect } from "react";
import {
  DollarSign,
  Download,
  Award,
  BarChart,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface QuotaDetails {
  used: number;
  limit: number;
  percentage: number;
}

interface BillingStatus {
  tenant_id: string;
  organization: string;
  plan: string;
  price_monthly: number;
  usage: {
    customers: QuotaDetails;
    workflows: QuotaDetails;
  };
}

interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: string;
  plan: string;
}

export default function BillingPage() {
  const [statusData, setStatusData] = useState<BillingStatus | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadBillingData = async () => {
    try {
      setLoading(true);
      setError("");

      const statusRes = await apiClient.get("/billing/status");
      setStatusData(statusRes.data);

      const invoiceRes = await apiClient.get("/billing/invoices");
      setInvoices(invoiceRes.data);
    } catch (err: any) {
      console.error("Failed to load billing metrics", err);
      setError("Failed to fetch billing data. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBillingData();
  }, []);

  const handleUpgrade = async (planName: string) => {
    try {
      setError("");
      setSuccess("");
      await apiClient.post("/billing/upgrade", { plan: planName });
      setSuccess(`Plan successfully changed to ${planName.toUpperCase()}!`);
      await loadBillingData();
    } catch (err: any) {
      setError("Failed to change plan. Please try again.");
    }
  };

  const handleDownloadInvoice = async (invoiceId: string) => {
    try {
      const res = await apiClient.get(
        `/billing/invoices/${invoiceId}/download`,
      );
      const element = document.createElement("a");
      const file = new Blob([res.data], { type: "text/plain" });
      element.href = URL.createObjectURL(file);
      element.download = `${invoiceId}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      setSuccess(`Downloaded receipt invoice: ${invoiceId}`);
    } catch (err: any) {
      setError("Failed to print invoice sheet.");
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500 dark:text-dark-muted font-medium">
        Loading billing data...
      </div>
    );
  }

  const currentPlan = statusData?.plan || "free";

  return (
    <div className="min-h-full space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-800 dark:text-white">
          Billing & Subscriptions
        </h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-dark-muted">
          Manage pricing options, billing limits, quota usage metering, and
          invoice downloads.
        </p>
      </div>

      {success && (
        <div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700 dark:border-emerald-950/20 dark:bg-emerald-950/20 dark:text-emerald-400">
          {success}
        </div>
      )}

      {error && (
        <div className="rounded-2xl border border-rose-100 bg-rose-50 p-4 text-sm font-semibold text-rose-700 dark:border-rose-950/20 dark:bg-rose-950/20 dark:text-rose-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left Column: Plan selector & progress limits */}
        <div className="lg:col-span-2 space-y-6">
          {/* Card: Current plan details */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2 dark:text-white">
              <Award className="h-5 w-5 text-blue-500" />
              Active Subscription
            </h2>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 bg-slate-50 rounded-2xl p-6 border border-slate-100 dark:bg-dark-bg/30 dark:border-dark-border">
              <div>
                <p className="text-xs font-bold text-slate-400 dark:text-dark-muted uppercase tracking-wider">
                  Current Plan
                </p>
                <p className="text-2xl font-bold text-slate-800 capitalize mt-1 dark:text-white">
                  {currentPlan} Plan
                </p>
                <p className="text-sm font-medium text-slate-500 dark:text-dark-muted mt-1">
                  Org: {statusData?.organization}
                </p>
              </div>
              <div className="sm:text-right shrink-0">
                <p className="text-xs font-bold text-slate-400 dark:text-dark-muted uppercase tracking-wider">
                  Monthly Charge
                </p>
                <p className="text-3xl font-extrabold text-slate-900 mt-1 dark:text-white">
                  ${statusData?.price_monthly}/mo
                </p>
              </div>
            </div>

            {/* Quota Progress meter bars */}
            <div className="mt-8 space-y-6">
              <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2 dark:text-white">
                <BarChart className="h-4 w-4 text-blue-500" />
                Usage Metering (Quotas)
              </h3>

              {statusData?.usage.customers && (
                <div>
                  <div className="flex justify-between text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    <span>Customers Active</span>
                    <span>
                      {statusData.usage.customers.used} /{" "}
                      {statusData.usage.customers.limit} (
                      {statusData.usage.customers.percentage}%)
                    </span>
                  </div>
                  <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden dark:bg-dark-bg">
                    <div
                      className={`h-full rounded-full ${statusData.usage.customers.percentage >= 90 ? "bg-rose-500" : "bg-blue-600"}`}
                      style={{
                        width: `${Math.min(statusData.usage.customers.percentage, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              )}

              {statusData?.usage.workflows && (
                <div>
                  <div className="flex justify-between text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    <span>Automation Workflows</span>
                    <span>
                      {statusData.usage.workflows.used} /{" "}
                      {statusData.usage.workflows.limit} (
                      {statusData.usage.workflows.percentage}%)
                    </span>
                  </div>
                  <div className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden dark:bg-dark-bg">
                    <div
                      className={`h-full rounded-full ${statusData.usage.workflows.percentage >= 90 ? "bg-rose-500" : "bg-blue-600"}`}
                      style={{
                        width: `${Math.min(statusData.usage.workflows.percentage, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Pricing options plans card */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Plan Card: Free */}
            <div
              className={`rounded-3xl border p-6 bg-white flex flex-col justify-between dark:bg-dark-bg/50 dark:backdrop-blur-xl ${currentPlan === "free" ? "border-blue-500 ring-1 ring-blue-500/20 dark:border-dark-accent dark:ring-dark-accent/20" : "border-slate-200 dark:border-dark-border"}`}
            >
              <div>
                <h3 className="font-bold text-slate-800 text-lg dark:text-white">Free</h3>
                <p className="text-xs font-semibold text-slate-400 dark:text-dark-muted mt-1">
                  For sandbox testing
                </p>
                <div className="my-6">
                  <span className="text-3xl font-extrabold text-slate-800 dark:text-white">
                    $0
                  </span>
                  <span className="text-slate-500 text-sm dark:text-dark-muted">/mo</span>
                </div>
                <ul className="text-xs font-medium text-slate-500 space-y-2 mb-6 dark:text-dark-muted">
                  <li>• Max 100 customers</li>
                  <li>• Max 5 workflows</li>
                  <li>• Standard LLM predictions</li>
                </ul>
              </div>
              <button
                disabled={currentPlan === "free"}
                onClick={() => handleUpgrade("free")}
                className="w-full rounded-xl bg-slate-100 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-200 disabled:opacity-50 dark:bg-dark-bg dark:text-slate-300 dark:hover:bg-dark-surface"
              >
                {currentPlan === "free" ? "Active Plan" : "Downgrade"}
              </button>
            </div>

            {/* Plan Card: Startup */}
            <div
              className={`rounded-3xl border p-6 bg-white flex flex-col justify-between dark:bg-dark-bg/50 dark:backdrop-blur-xl ${currentPlan === "startup" ? "border-blue-500 ring-1 ring-blue-500/20 dark:border-dark-accent dark:ring-dark-accent/20" : "border-slate-200 dark:border-dark-border"}`}
            >
              <div>
                <h3 className="font-bold text-slate-800 text-lg dark:text-white">Startup</h3>
                <p className="text-xs font-semibold text-slate-400 dark:text-dark-muted mt-1">
                  For growing teams
                </p>
                <div className="my-6">
                  <span className="text-3xl font-extrabold text-slate-800 dark:text-white">
                    $99
                  </span>
                  <span className="text-slate-500 text-sm dark:text-dark-muted">/mo</span>
                </div>
                <ul className="text-xs font-medium text-slate-500 space-y-2 mb-6 dark:text-dark-muted">
                  <li>• Max 1,000 customers</li>
                  <li>• Max 20 workflows</li>
                  <li>• Priority SLA chat limits</li>
                </ul>
              </div>
              <button
                disabled={currentPlan === "startup"}
                onClick={() => handleUpgrade("startup")}
                className="w-full rounded-xl bg-blue-600 py-2.5 text-xs font-bold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {currentPlan === "startup" ? "Active Plan" : "Select Startup"}
              </button>
            </div>

            {/* Plan Card: Enterprise */}
            <div
              className={`rounded-3xl border p-6 bg-white flex flex-col justify-between dark:bg-dark-bg/50 dark:backdrop-blur-xl ${currentPlan === "enterprise" ? "border-blue-500 ring-1 ring-blue-500/20 dark:border-dark-accent dark:ring-dark-accent/20" : "border-slate-200 dark:border-dark-border"}`}
            >
              <div>
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-slate-800 text-lg dark:text-white">
                    Enterprise
                  </h3>
                  <span className="bg-purple-100 text-purple-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase dark:bg-purple-900/30 dark:text-purple-300">
                    VIP
                  </span>
                </div>
                <p className="text-xs font-semibold text-slate-400 dark:text-dark-muted mt-1">
                  For full orchestration
                </p>
                <div className="my-6">
                  <span className="text-3xl font-extrabold text-slate-800 dark:text-white">
                    $499
                  </span>
                  <span className="text-slate-500 text-sm dark:text-dark-muted">/mo</span>
                </div>
                <ul className="text-xs font-medium text-slate-500 space-y-2 mb-6 dark:text-dark-muted">
                  <li>• Unlimited customers</li>
                  <li>• Unlimited workflows</li>
                  <li>• Custom AI Agents support</li>
                </ul>
              </div>
              <button
                disabled={currentPlan === "enterprise"}
                onClick={() => handleUpgrade("enterprise")}
                className="w-full rounded-xl bg-slate-900 py-2.5 text-xs font-bold text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-dark-bg dark:hover:bg-dark-surface dark:text-slate-200"
              >
                {currentPlan === "enterprise" ? "Active Plan" : "Upgrade VIP"}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Invoices List */}
        <div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
            <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2 dark:text-white">
              <DollarSign className="h-5 w-5 text-blue-500" />
              Invoices History
            </h2>
            <div className="divide-y divide-slate-100 dark:divide-dark-border">
              {invoices.length === 0 ? (
                <p className="text-sm font-medium text-slate-400 dark:text-dark-muted py-4 text-center">
                  No payment history found.
                </p>
              ) : (
                invoices.map((inv) => (
                  <div
                    key={inv.id}
                    className="flex justify-between items-center py-4"
                  >
                    <div>
                      <p className="text-sm font-bold text-slate-800 dark:text-white">
                        {inv.id}
                      </p>
                      <p className="text-xs font-medium text-slate-400 dark:text-dark-muted mt-0.5">
                        {inv.date}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-bold text-slate-800 dark:text-white">
                          ${inv.amount}.00
                        </p>
                        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full capitalize dark:bg-emerald-950/20 dark:text-emerald-400">
                          {inv.status}
                        </span>
                      </div>
                      <button
                        onClick={() => handleDownloadInvoice(inv.id)}
                        className="rounded-xl border border-slate-200 p-2 text-slate-500 hover:bg-slate-50 dark:border-dark-border dark:text-slate-400 dark:hover:bg-dark-bg"
                        title="Download Invoice"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
