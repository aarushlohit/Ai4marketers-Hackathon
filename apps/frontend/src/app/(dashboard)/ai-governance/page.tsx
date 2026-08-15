"use client";

import { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface AIRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  hasThreshold?: boolean;
  threshold?: number;
}

type Initiator = "AI" | "User";

interface AuditEntry {
  id: number;
  action: string;
  target: string;
  reason: string;
  time: string;
  initiator: Initiator;
}

// ─── Mock Data ────────────────────────────────────────────────────────────────

const INITIAL_RULES: AIRule[] = [
  {
    id: "churn-rec",
    name: "Auto-generate churn recommendations",
    description:
      "AI will automatically generate churn risk scores and retention recommendations for at-risk accounts.",
    enabled: true,
    hasThreshold: true,
    threshold: 75,
  },
  {
    id: "auto-email",
    name: "Auto-send retention emails",
    description:
      "Automatically send pre-approved retention offer emails when churn probability exceeds the threshold.",
    enabled: false,
    hasThreshold: true,
    threshold: 85,
  },
  {
    id: "data-access",
    name: "AI copilot can access customer data",
    description:
      "Allow the AI Copilot to read customer profiles, interaction history, and health scores during sessions.",
    enabled: true,
  },
  {
    id: "auto-accept",
    name: "Auto-accept high-confidence recommendations",
    description:
      "Automatically apply AI recommendations that exceed the confidence threshold without human review.",
    enabled: false,
    hasThreshold: true,
    threshold: 92,
  },
  {
    id: "workflow-trigger",
    name: "AI can trigger workflow automations",
    description:
      "Allow AI to initiate pre-defined workflow automations such as alerts, task creation, and escalations.",
    enabled: true,
  },
];

const AUDIT_ENTRIES: AuditEntry[] = [
  {
    id: 1,
    action: "Recommendation Generated",
    target: "Emily Chen",
    reason: "91% churn risk",
    time: "2 min ago",
    initiator: "AI",
  },
  {
    id: 2,
    action: "Workflow Triggered",
    target: "TechGlobal",
    reason: "Health drop alert",
    time: "15 min ago",
    initiator: "AI",
  },
  {
    id: 3,
    action: "Email Sent",
    target: "Marcus Johnson",
    reason: "Retention offer",
    time: "1 hr ago",
    initiator: "AI",
  },
  {
    id: 4,
    action: "Recommendation Rejected",
    target: "Zara Khan",
    reason: "User rejected",
    time: "2 hrs ago",
    initiator: "User",
  },
  {
    id: 5,
    action: "Prediction Updated",
    target: "All customers",
    reason: "Scheduled refresh",
    time: "3 hrs ago",
    initiator: "AI",
  },
];

// ─── Toggle Component ─────────────────────────────────────────────────────────

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 flex-shrink-0 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 dark:focus:ring-offset-dark-surface ${
        checked ? "bg-sky-500" : "bg-slate-200 dark:bg-slate-700"
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
          checked ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

// ─── Tab 1: AI Policy Rules ───────────────────────────────────────────────────

function AIPolicyTab() {
  const [rules, setRules] = useState<AIRule[]>(INITIAL_RULES);

  const toggleRule = (id: string) =>
    setRules((prev) =>
      prev.map((r) => (r.id === id ? { ...r, enabled: !r.enabled } : r))
    );

  const updateThreshold = (id: string, value: number) =>
    setRules((prev) =>
      prev.map((r) => (r.id === id ? { ...r, threshold: value } : r))
    );

  return (
    <div className="space-y-3">
      {rules.map((rule) => (
        <div
          key={rule.id}
          className={`rounded-xl border p-5 shadow-sm transition-all ${
            rule.enabled
              ? "border-sky-200 bg-sky-50/30 dark:border-sky-500/20 dark:bg-sky-500/5"
              : "border-slate-200 bg-white dark:border-dark-border dark:bg-dark-surface"
          }`}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  {rule.name}
                </h3>
                {rule.enabled ? (
                  <span className="inline-flex items-center rounded-full bg-sky-100 dark:bg-sky-500/20 px-2 py-0.5 text-xs font-medium text-sky-700 dark:text-sky-400">
                    Enabled
                  </span>
                ) : (
                  <span className="inline-flex items-center rounded-full bg-slate-100 dark:bg-slate-700/50 px-2 py-0.5 text-xs font-medium text-slate-500 dark:text-slate-400">
                    Disabled
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                {rule.description}
              </p>
              {rule.hasThreshold && rule.enabled && (
                <div className="mt-3 flex items-center gap-3">
                  <label className="text-xs text-slate-500 dark:text-slate-400 font-medium whitespace-nowrap">
                    Confidence threshold:
                  </label>
                  <input
                    type="number"
                    min={50}
                    max={99}
                    value={rule.threshold}
                    onChange={(e) =>
                      updateThreshold(rule.id, Number(e.target.value))
                    }
                    className="w-20 rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-bg px-2 py-1 text-sm text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500 text-center"
                  />
                  <span className="text-xs text-slate-500 dark:text-slate-400">%</span>
                </div>
              )}
            </div>
            <Toggle checked={rule.enabled} onChange={() => toggleRule(rule.id)} />
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Tab 2: AI Audit Trail ────────────────────────────────────────────────────

function AIAuditTrailTab() {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-dark-border overflow-hidden shadow-sm">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-dark-border">
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              Action
            </th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              Target
            </th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              Reason
            </th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              Time
            </th>
            <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              Initiated By
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-dark-surface divide-y divide-slate-100 dark:divide-dark-border">
          {AUDIT_ENTRIES.map((entry) => (
            <tr
              key={entry.id}
              className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
            >
              <td className="px-4 py-3 font-medium text-slate-800 dark:text-slate-200">
                {entry.action}
              </td>
              <td className="px-4 py-3 text-slate-600 dark:text-slate-400 text-sm">
                {entry.target}
              </td>
              <td className="px-4 py-3 text-slate-500 dark:text-slate-500 text-xs italic">
                {entry.reason}
              </td>
              <td className="px-4 py-3 text-slate-500 dark:text-slate-500 text-xs">
                {entry.time}
              </td>
              <td className="px-4 py-3">
                {entry.initiator === "AI" ? (
                  <span className="inline-flex items-center gap-1 rounded-full bg-violet-50 dark:bg-violet-500/10 px-2 py-0.5 text-xs font-semibold text-violet-700 dark:text-violet-400">
                    <span className="text-[10px]">🤖</span> AI
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 dark:bg-slate-700/50 px-2 py-0.5 text-xs font-semibold text-slate-600 dark:text-slate-400">
                    <span className="text-[10px]">👤</span> User
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Tab 3: Guardrails & Limits ───────────────────────────────────────────────

const RESTRICTED_FIELDS = ["SSN", "Credit Score", "Medical Info"] as const;
type RestrictedField = (typeof RESTRICTED_FIELDS)[number];

function GuardrailsTab({
  emergencyStop,
  setEmergencyStop,
}: {
  emergencyStop: boolean;
  setEmergencyStop: (val: boolean) => void;
}) {
  const [maxRecs, setMaxRecs] = useState(3);
  const [minConfidence, setMinConfidence] = useState(80);
  const [timeout, setTimeout_] = useState("10");
  const [restricted, setRestricted] = useState<Set<RestrictedField>>(
    new Set(["SSN", "Medical Info"])
  );

  const toggleRestricted = (field: RestrictedField) => {
    setRestricted((prev) => {
      const next = new Set(prev);
      if (next.has(field)) next.delete(field);
      else next.add(field);
      return next;
    });
  };

  return (
    <div className="space-y-4">
      {/* Max Recommendations */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-1">
          <span className="text-base">📊</span> Max Recommendations per Customer / Day
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          Limit how many AI-generated recommendations can be surfaced per customer within a 24-hour
          window.
        </p>
        <div className="flex items-center gap-3">
          <input
            type="number"
            min={1}
            max={20}
            value={maxRecs}
            onChange={(e) => setMaxRecs(Number(e.target.value))}
            className="w-24 rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-bg px-3 py-2 text-sm text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500 text-center"
          />
          <span className="text-xs text-slate-500 dark:text-slate-400">recommendations per day</span>
        </div>
      </div>

      {/* Confidence Threshold */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-1">
          <span className="text-base">🎯</span> Min Confidence Threshold for Auto-Actions
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          AI will only autonomously act when its confidence score meets or exceeds this threshold.
        </p>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min={50}
            max={99}
            value={minConfidence}
            onChange={(e) => setMinConfidence(Number(e.target.value))}
            className="flex-1 accent-sky-500 cursor-pointer"
          />
          <span className="w-14 text-center rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-bg px-2 py-1 text-sm font-semibold text-slate-800 dark:text-white">
            {minConfidence}%
          </span>
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs text-slate-400 dark:text-slate-500">50% (Lenient)</span>
          <span className="text-xs text-slate-400 dark:text-slate-500">99% (Strict)</span>
        </div>
      </div>

      {/* Restricted Data Fields */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-1">
          <span className="text-base">🚫</span> Restricted Data Fields
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          Prevent the AI Copilot from accessing or referencing these sensitive data fields in
          recommendations or outputs.
        </p>
        <div className="flex flex-col gap-2.5">
          {RESTRICTED_FIELDS.map((field) => (
            <label
              key={field}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <input
                type="checkbox"
                checked={restricted.has(field)}
                onChange={() => toggleRestricted(field)}
                className="h-4 w-4 rounded border-slate-300 text-sky-500 focus:ring-sky-500 dark:border-slate-600 dark:bg-dark-bg cursor-pointer"
              />
              <span className="text-sm text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
                {field}
              </span>
              {restricted.has(field) && (
                <span className="text-xs text-red-500 dark:text-red-400 font-medium">
                  Restricted
                </span>
              )}
            </label>
          ))}
        </div>
      </div>

      {/* AI Response Timeout */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-1">
          <span className="text-base">⏱</span> AI Response Timeout
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          Maximum wait time for an AI inference response before the request is cancelled and
          flagged.
        </p>
        <select
          value={timeout}
          onChange={(e) => setTimeout_(e.target.value)}
          className="w-full sm:w-48 rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-bg px-3 py-2 text-sm text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <option value="5">5 seconds</option>
          <option value="10">10 seconds</option>
          <option value="30">30 seconds</option>
          <option value="60">60 seconds</option>
        </select>
      </div>

      {/* Emergency Stop */}
      <div
        className={`rounded-xl border-2 p-5 shadow-sm transition-all ${
          emergencyStop
            ? "border-red-400 bg-red-50 dark:bg-red-500/10 dark:border-red-500/50"
            : "border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface"
        }`}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3
              className={`text-sm font-semibold flex items-center gap-2 ${
                emergencyStop
                  ? "text-red-700 dark:text-red-400"
                  : "text-slate-900 dark:text-white"
              }`}
            >
              <span className="text-base">🛑</span> Emergency Stop
            </h3>
            <p
              className={`text-xs mt-1 ${
                emergencyStop
                  ? "text-red-600 dark:text-red-400"
                  : "text-slate-500 dark:text-slate-400"
              }`}
            >
              Immediately halt all autonomous AI actions across the platform. Human review will be
              required for every AI-suggested action until this is disabled.
            </p>
          </div>
          <button
            onClick={() => setEmergencyStop(!emergencyStop)}
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-sm ${
              emergencyStop
                ? "bg-red-600 hover:bg-red-700 text-white ring-2 ring-red-400 ring-offset-2 dark:ring-offset-dark-surface"
                : "bg-red-500 hover:bg-red-600 text-white"
            }`}
          >
            {emergencyStop ? "✓ AI Stopped — Click to Resume" : "Engage Emergency Stop"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

const TABS = ["AI Policy Rules", "AI Audit Trail", "Guardrails & Limits"] as const;
type Tab = (typeof TABS)[number];

export default function AIGovernancePage() {
  const [activeTab, setActiveTab] = useState<Tab>("AI Policy Rules");
  const [emergencyStop, setEmergencyStop] = useState(false);

  return (
    <div className="p-8 space-y-6 max-w-5xl">
      {/* Emergency Stop Banner */}
      {emergencyStop && (
        <div className="flex items-center justify-between rounded-xl border border-red-400 dark:border-red-500/50 bg-red-50 dark:bg-red-500/10 px-5 py-4 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="text-xl">🛑</span>
            <div>
              <p className="text-sm font-bold text-red-700 dark:text-red-400">
                Emergency Stop is Active
              </p>
              <p className="text-xs text-red-600 dark:text-red-400 mt-0.5">
                All autonomous AI actions are suspended. Manual review required for every AI
                recommendation.
              </p>
            </div>
          </div>
          <button
            onClick={() => setEmergencyStop(false)}
            className="px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-semibold transition-colors"
          >
            Resume AI
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Governance</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Configure AI boundaries, review automated decisions, and manage guardrails for the AI
            Copilot.
          </p>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold border ${
            emergencyStop
              ? "bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 border-red-200 dark:border-red-500/20"
              : "bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-400 border-violet-200 dark:border-violet-500/20"
          }`}
        >
          <span
            className={`h-2 w-2 rounded-full ${
              emergencyStop ? "bg-red-500 animate-pulse" : "bg-violet-500 animate-pulse"
            }`}
          />
          {emergencyStop ? "AI Suspended" : "AI Active"}
        </span>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-slate-200 dark:border-dark-border">
        <nav className="-mb-px flex gap-6">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab
                  ? "border-sky-500 text-sky-600 dark:text-sky-400"
                  : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === "AI Policy Rules" && <AIPolicyTab />}
        {activeTab === "AI Audit Trail" && <AIAuditTrailTab />}
        {activeTab === "Guardrails & Limits" && (
          <GuardrailsTab
            emergencyStop={emergencyStop}
            setEmergencyStop={setEmergencyStop}
          />
        )}
      </div>
    </div>
  );
}
