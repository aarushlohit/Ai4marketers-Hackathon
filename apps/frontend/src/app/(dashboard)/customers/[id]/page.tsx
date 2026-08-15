"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import {
  Activity,
  AlertTriangle,
  Briefcase,
  Calendar,
  MessageSquare,
  TrendingDown,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface Customer {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  company: string | null;
  status: string;
  health_score: number | null;
  churn_probability: number | null;
  lead_score: number | null;
  lifetime_value: number | null;
  crm_source: string | null;
}

export default function Customer360Page({
  params,
}: {
  params: { id: string };
}) {
  const { data: customer, isLoading, error } = useQuery<Customer>({
    queryKey: ["customer", params.id],
    queryFn: () =>
      apiClient.get(`/customers/${params.id}`).then((res) => res.data),
  });

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
      </div>
    );
  }

  if (error || !customer) {
    return (
      <div className="rounded-2xl border border-red-200 bg-white p-6 text-red-700 dark:border-dark-border dark:bg-black dark:text-red-400">
        <h3 className="font-semibold">Failed to load customer profile</h3>
        <p className="mt-1 text-sm">Please verify the URL or try again later.</p>
      </div>
    );
  }

  const fullName = `${customer.first_name} ${customer.last_name}`;
  const companyName = customer.company || "Independent Customer";
  const health = customer.health_score ?? 0;
  const churn = customer.churn_probability ?? 0;
  const churnPct = Math.round(churn * 100);
  const ltv = customer.lifetime_value || health * 1500;

  // Determine health style
  let healthColor = "text-amber-500";
  let healthLabel = "Fair";
  if (health >= 85) {
    healthColor = "text-emerald-500";
    healthLabel = "Excellent";
  } else if (health >= 70) {
    healthColor = "text-teal-500";
    healthLabel = "Good";
  } else if (health < 40) {
    healthColor = "text-rose-500";
    healthLabel = "Critical";
  } else if (health < 55) {
    healthColor = "text-orange-500";
    healthLabel = "Poor";
  }

  // Determine churn style
  const isHighRisk = churn >= 0.7;
  const churnRiskLabel = isHighRisk ? "high risk of churn" : churn >= 0.4 ? "moderate risk of churn" : "low risk of churn";
  const churnRiskColor = isHighRisk ? "text-rose-500 dark:text-rose-400" : churn >= 0.4 ? "text-amber-500" : "text-emerald-500";

  return (
    <div className="min-h-full space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-800 dark:text-white">
          Customer 360: {fullName}
        </h1>
        <p className="mt-2 text-slate-500 dark:text-dark-muted">
          Comprehensive AI analysis of {customer.crm_source || "CRM"} data for {companyName}.
        </p>
      </div>

      {/* AI Summary Banner - monochrome black/white */}
      <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white p-6 dark:border-dark-border dark:bg-black backdrop-blur-xl">
        <div className="flex items-start gap-4">
          <div className="rounded-2xl border border-slate-100 p-3 text-slate-700 dark:border-dark-border dark:text-slate-300">
            <MessageSquare className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800 dark:text-white">
              AI Executive Summary
            </h2>
            <p className="mt-2 text-slate-600 dark:text-slate-300 leading-relaxed">
              {fullName} is a customer at {companyName} currently classified at{" "}
              <strong className={churnRiskColor}>{churnRiskLabel} ({churnPct}% probability)</strong>. 
              The health score is <strong className={healthColor}>{health} ({healthLabel})</strong>.
              {isHighRisk 
                ? " Direct customer success outreach is recommended to address potential onboarding blockers." 
                : " Overall metrics are stable. Focus should remain on nurturing key stakeholders for expansion opportunities."}
              <br />
              <br />
              <strong>Next Best Action:</strong> {isHighRisk 
                ? "Schedule an urgent technical alignment meeting to address key support bottlenecks." 
                : "Deliver the newly launched product catalog to explore potential upsell opportunities."}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Intelligence Column */}
        <div className="space-y-6 lg:col-span-1">
          {/* Health Score */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-black backdrop-blur-xl">
            <h3 className="text-sm font-medium text-slate-400 dark:text-dark-muted mb-4">
              Customer Health Score
            </h3>
            <div className="flex items-end justify-between">
              <div className={`text-5xl font-bold ${healthColor}`}>
                {health}<span className="text-2xl text-slate-300 dark:text-dark-border">/100</span>
              </div>
              <div className={`flex items-center px-2 py-1 rounded-lg text-sm ${health >= 70 ? "text-emerald-500 bg-emerald-500/10" : "text-rose-500 bg-rose-500/10"}`}>
                {health >= 70 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                {health >= 70 ? "+5 pts" : "-12 pts"}
              </div>
            </div>
            <div className="mt-6 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 dark:text-dark-muted">Product Usage</span>
                <span className={`${healthColor} font-medium`}>{healthLabel}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 dark:text-dark-muted">Support Tickets</span>
                <span className="text-slate-600 dark:text-slate-300 font-medium">None Open</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 dark:text-dark-muted">NPS Score</span>
                <span className="text-emerald-500 font-medium">8 (Promoter)</span>
              </div>
            </div>
          </div>

          {/* Predictions */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-black backdrop-blur-xl">
            <h3 className="text-sm font-medium text-slate-400 dark:text-dark-muted mb-4">
              ML Predictions
            </h3>
            <div className="space-y-4">
              <div className="p-4 rounded-2xl border border-slate-100 bg-slate-50 dark:bg-dark-bg/30 dark:border-dark-border">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className={`h-4 w-4 ${churnRiskColor}`} />
                  <span className="font-semibold text-slate-700 dark:text-white">
                    Churn Probability: {churnPct}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-dark-bg rounded-full h-2">
                  <div className={`h-2 rounded-full ${isHighRisk ? "bg-rose-500" : churn >= 0.4 ? "bg-amber-500" : "bg-emerald-500"}`} style={{ width: `${churnPct}%` }}></div>
                </div>
              </div>
              <div className="p-4 rounded-2xl border border-slate-100 bg-slate-50 dark:bg-dark-bg/30 dark:border-dark-border">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-emerald-500" />
                  <span className="font-semibold text-slate-700 dark:text-white">
                    Predicted LTV: {formatCurrency(ltv)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Timeline & Deals Column */}
        <div className="space-y-6 lg:col-span-2">
          {/* Deal History */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-black backdrop-blur-xl">
            <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-blue-500" /> Deal History
            </h3>
            <div className="overflow-hidden rounded-2xl border border-slate-100 dark:border-dark-border">
              <table className="w-full text-left text-sm text-slate-600 dark:text-slate-400">
                <thead className="bg-slate-50 uppercase dark:bg-dark-bg/50">
                  <tr>
                    <th className="px-4 py-3 font-medium text-slate-400 dark:text-dark-muted">
                      Deal Name
                    </th>
                    <th className="px-4 py-3 font-medium text-slate-400 dark:text-dark-muted">
                      Amount
                    </th>
                    <th className="px-4 py-3 font-medium text-slate-400 dark:text-dark-muted">
                      Stage
                    </th>
                    <th className="px-4 py-3 font-medium text-slate-400 dark:text-dark-muted">
                      Close Date
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-dark-border">
                  <tr>
                    <td className="px-4 py-3 text-slate-800 dark:text-white font-medium">
                      Enterprise Tier License
                    </td>
                    <td className="px-4 py-3">$45,000</td>
                    <td className="px-4 py-3">
                      <span className="text-emerald-600 bg-emerald-500/10 px-2 py-1 rounded-md text-xs font-semibold">
                        Closed Won
                      </span>
                    </td>
                    <td className="px-4 py-3">Oct 12, 2025</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-3 text-slate-800 dark:text-white font-medium">
                      Custom Integration Setup
                    </td>
                    <td className="px-4 py-3">$15,000</td>
                    <td className="px-4 py-3">
                      <span className="text-blue-600 bg-blue-500/10 px-2 py-1 rounded-md text-xs font-semibold">
                        Negotiation
                      </span>
                    </td>
                    <td className="px-4 py-3">Est. Jul 30, 2026</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Activity Timeline */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm dark:border-dark-border dark:bg-black backdrop-blur-xl">
            <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-6 flex items-center gap-2">
              <Calendar className="h-5 w-5 text-purple-500" /> Activity Timeline
            </h3>
            <div className="relative border-l border-slate-100 dark:border-dark-border ml-3 space-y-8">
              <div className="relative pl-6">
                <span className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-blue-500 ring-4 ring-white dark:ring-black"></span>
                <p className="text-sm font-semibold text-slate-800 dark:text-white">
                  Meeting Scheduled: Q3 Review
                </p>
                <p className="text-xs text-slate-400 dark:text-dark-muted mt-1">Today at 2:00 PM</p>
              </div>
              <div className="relative pl-6">
                <span className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-emerald-500 ring-4 ring-white dark:ring-black"></span>
                <p className="text-sm font-semibold text-slate-800 dark:text-white">
                  Email Opened: &quot;New Features Update&quot;
                </p>
                <p className="text-xs text-slate-400 dark:text-dark-muted mt-1">
                  Yesterday at 10:15 AM
                </p>
              </div>
              <div className="relative pl-6">
                <span className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full bg-rose-500 ring-4 ring-white dark:ring-black"></span>
                <p className="text-sm font-semibold text-slate-800 dark:text-white">
                  Support Ticket #8843 Created
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Issue with API rate limits impacting their syncing process.
                </p>
                <p className="text-xs text-slate-400 dark:text-dark-muted mt-1">Jul 12, 2026</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
