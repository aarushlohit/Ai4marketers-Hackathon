"use client";

import { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

type AuditStatus = "Success" | "Failed" | "Warning";
type ComplianceStatus = "Active" | "Monitoring" | "Pending";
type FilterTab = "All" | AuditStatus;

interface AuditRow {
  id: number;
  event: string;
  actor: string;
  time: string;
  status: AuditStatus;
}

interface ComplianceCard {
  id: string;
  title: string;
  description: string;
  status: ComplianceStatus;
  detail: string;
}

// ─── Mock Data ────────────────────────────────────────────────────────────────

const COMPLIANCE_CARDS: ComplianceCard[] = [
  {
    id: "gdpr",
    title: "GDPR",
    description:
      "General Data Protection Regulation compliance for EU customer data processing and privacy rights.",
    status: "Active",
    detail: "Last audited 3 days ago",
  },
  {
    id: "soc2",
    title: "SOC 2",
    description:
      "Service Organization Control 2 — security, availability, and confidentiality trust service criteria.",
    status: "Monitoring",
    detail: "Audit in progress",
  },
  {
    id: "hipaa",
    title: "HIPAA",
    description:
      "Health Insurance Portability and Accountability Act — applicable if health data is processed.",
    status: "Pending",
    detail: "Configuration required",
  },
];

const AUDIT_ROWS: AuditRow[] = [
  { id: 1, event: "User Login", actor: "admin@example.com", time: "2 min ago", status: "Success" },
  { id: 2, event: "CRM Sync", actor: "HubSpot", time: "15 min ago", status: "Success" },
  { id: 3, event: "Password Change", actor: "user@example.com", time: "1 hr ago", status: "Success" },
  { id: 4, event: "Failed Login", actor: "unknown@test.com", time: "2 hrs ago", status: "Failed" },
  { id: 5, event: "API Access", actor: "External App", time: "3 hrs ago", status: "Success" },
  { id: 6, event: "Data Export", actor: "admin@example.com", time: "1 day ago", status: "Warning" },
];

const DEFAULT_IPS = ["192.168.1.1", "10.0.0.15", "203.0.113.42"];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function statusDotClass(status: ComplianceStatus) {
  return status === "Active"
    ? "bg-emerald-500"
    : status === "Monitoring"
    ? "bg-amber-400"
    : "bg-slate-400";
}

function statusBadgeClass(status: ComplianceStatus) {
  return status === "Active"
    ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
    : status === "Monitoring"
    ? "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400"
    : "bg-slate-100 text-slate-600 dark:bg-slate-700/50 dark:text-slate-400";
}

function auditBadgeClass(status: AuditStatus) {
  return status === "Success"
    ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400"
    : status === "Failed"
    ? "bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400"
    : "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400";
}

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

// ─── Tab 1: Compliance Status ─────────────────────────────────────────────────

function ComplianceTab() {
  const [toggles, setToggles] = useState<Record<string, boolean>>({
    gdpr: true,
    soc2: true,
    hipaa: false,
  });

  const toggle = (id: string) =>
    setToggles((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-dark-border dark:bg-dark-surface">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Overall Compliance Score
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Based on active framework adherence
            </p>
          </div>
          <span className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">87%</span>
        </div>
        <div className="w-full h-2.5 rounded-full bg-slate-100 dark:bg-slate-700">
          <div
            className="h-2.5 rounded-full bg-gradient-to-r from-emerald-400 to-emerald-600 transition-all"
            style={{ width: "87%" }}
          />
        </div>
        <p className="mt-2 text-xs text-slate-400 dark:text-slate-500">
          13% remaining — complete HIPAA configuration to improve score
        </p>
      </div>

      {/* Compliance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {COMPLIANCE_CARDS.map((card) => (
          <div
            key={card.id}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-dark-border dark:bg-dark-surface flex flex-col gap-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${statusDotClass(card.status)}`} />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  {card.title}
                </h3>
              </div>
              <Toggle checked={toggles[card.id]} onChange={() => toggle(card.id)} />
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
              {card.description}
            </p>
            <div className="flex items-center justify-between mt-auto pt-1">
              <span
                className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${statusBadgeClass(
                  card.status
                )}`}
              >
                {card.status}
              </span>
              <span className="text-xs text-slate-400 dark:text-slate-500">{card.detail}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Tab 2: Audit Logs ────────────────────────────────────────────────────────

function AuditLogsTab() {
  const [filter, setFilter] = useState<FilterTab>("All");

  const filtered =
    filter === "All" ? AUDIT_ROWS : AUDIT_ROWS.filter((r) => r.status === filter);

  const tabs: FilterTab[] = ["All", "Success", "Failed", "Warning"];

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex gap-1 rounded-lg bg-slate-100 dark:bg-dark-surface p-1 w-fit border border-slate-200 dark:border-dark-border">
        {tabs.map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              filter === t
                ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
            }`}
          >
            {t}
            <span
              className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${
                filter === t
                  ? "bg-sky-100 text-sky-700 dark:bg-sky-500/20 dark:text-sky-400"
                  : "bg-slate-200 text-slate-500 dark:bg-slate-600 dark:text-slate-400"
              }`}
            >
              {t === "All"
                ? AUDIT_ROWS.length
                : AUDIT_ROWS.filter((r) => r.status === t).length}
            </span>
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border overflow-hidden shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-dark-border">
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Event
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Actor
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Time
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-dark-surface divide-y divide-slate-100 dark:divide-dark-border">
            {filtered.map((row) => (
              <tr
                key={row.id}
                className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
              >
                <td className="px-4 py-3 font-medium text-slate-800 dark:text-slate-200">
                  {row.event}
                </td>
                <td className="px-4 py-3 text-slate-600 dark:text-slate-400 font-mono text-xs">
                  {row.actor}
                </td>
                <td className="px-4 py-3 text-slate-500 dark:text-slate-500 text-xs">
                  {row.time}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold ${auditBadgeClass(
                      row.status
                    )}`}
                  >
                    <span
                      className={`mr-1.5 h-1.5 w-1.5 rounded-full ${
                        row.status === "Success"
                          ? "bg-emerald-500"
                          : row.status === "Failed"
                          ? "bg-red-500"
                          : "bg-amber-400"
                      }`}
                    />
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td
                  colSpan={4}
                  className="px-4 py-8 text-center text-sm text-slate-400 dark:text-slate-500"
                >
                  No events match the selected filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── Tab 3: Data Security ─────────────────────────────────────────────────────

function DataSecurityTab() {
  const [encryptionEnabled, setEncryptionEnabled] = useState(true);
  const [twoFAEnabled, setTwoFAEnabled] = useState(false);
  const [retention, setRetention] = useState("90");
  const [allowedIPs, setAllowedIPs] = useState<string[]>(DEFAULT_IPS);
  const [ipInput, setIpInput] = useState("");

  const addIP = () => {
    const trimmed = ipInput.trim();
    if (trimmed && !allowedIPs.includes(trimmed)) {
      setAllowedIPs((prev) => [...prev, trimmed]);
      setIpInput("");
    }
  };

  const removeIP = (ip: string) => setAllowedIPs((prev) => prev.filter((x) => x !== ip));

  return (
    <div className="space-y-4">
      {/* Encryption */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <span className="text-base">🔒</span> Data Encryption
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              AES-256 encryption for all stored customer and CRM data. Recommended to keep enabled at
              all times.
            </p>
          </div>
          <Toggle checked={encryptionEnabled} onChange={() => setEncryptionEnabled((v) => !v)} />
        </div>
        {encryptionEnabled && (
          <div className="mt-3 flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg px-3 py-2">
            <span>✓</span>
            <span>AES-256 encryption is active. All data is encrypted at rest and in transit.</span>
          </div>
        )}
      </div>

      {/* Data Retention */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-1">
          <span className="text-base">📅</span> Data Retention Policy
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          Set how long activity logs and customer interaction data are retained before being purged.
        </p>
        <select
          value={retention}
          onChange={(e) => setRetention(e.target.value)}
          className="w-full sm:w-64 rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-bg px-3 py-2 text-sm text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <option value="30">30 days</option>
          <option value="90">90 days</option>
          <option value="365">1 year</option>
          <option value="forever">Forever</option>
        </select>
        <p className="mt-2 text-xs text-slate-400 dark:text-slate-500">
          Current policy:{" "}
          <span className="font-medium text-slate-600 dark:text-slate-300">
            {retention === "forever" ? "Forever" : `${retention} days`}
          </span>
        </p>
      </div>

      {/* IP Allowlist */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-1">
          <span className="text-base">🌐</span> IP Allowlist
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
          Restrict admin dashboard access to specific IP addresses.
        </p>
        <div className="flex gap-2 mb-3">
          <input
            type="text"
            value={ipInput}
            onChange={(e) => setIpInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addIP()}
            placeholder="e.g. 192.168.1.100"
            className="flex-1 rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-bg px-3 py-2 text-sm text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
          <button
            onClick={addIP}
            className="px-4 py-2 rounded-lg bg-sky-500 text-white text-sm font-medium hover:bg-sky-600 transition-colors"
          >
            Add IP
          </button>
        </div>
        <div className="space-y-2">
          {allowedIPs.map((ip) => (
            <div
              key={ip}
              className="flex items-center justify-between rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-dark-border px-3 py-2"
            >
              <span className="font-mono text-sm text-slate-700 dark:text-slate-300">{ip}</span>
              <button
                onClick={() => removeIP(ip)}
                className="text-xs text-red-500 hover:text-red-700 dark:hover:text-red-400 font-medium transition-colors"
              >
                Remove
              </button>
            </div>
          ))}
          {allowedIPs.length === 0 && (
            <p className="text-xs text-slate-400 dark:text-slate-500 italic">
              No IPs in allowlist — all IPs are permitted.
            </p>
          )}
        </div>
      </div>

      {/* 2FA */}
      <div className="rounded-xl border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface p-5 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <span className="text-base">🔑</span> Enforce 2FA for All Users
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Require two-factor authentication for every user in your organization. Users without 2FA
              will be prompted to set it up on next login.
            </p>
          </div>
          <Toggle checked={twoFAEnabled} onChange={() => setTwoFAEnabled((v) => !v)} />
        </div>
        {twoFAEnabled && (
          <div className="mt-3 flex items-center gap-2 text-xs text-sky-600 dark:text-sky-400 bg-sky-50 dark:bg-sky-500/10 rounded-lg px-3 py-2">
            <span>ℹ</span>
            <span>
              2FA enforcement is enabled. Users without 2FA will be locked out until they enroll.
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

const TABS = ["Compliance", "Audit Logs", "Data Security"] as const;
type Tab = (typeof TABS)[number];

export default function SecurityCenterPage() {
  const [activeTab, setActiveTab] = useState<Tab>("Compliance");

  return (
    <div className="p-8 space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Security Center</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Manage compliance frameworks, review audit logs, and configure data security policies.
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 dark:bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          Monitoring Active
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
        {activeTab === "Compliance" && <ComplianceTab />}
        {activeTab === "Audit Logs" && <AuditLogsTab />}
        {activeTab === "Data Security" && <DataSecurityTab />}
      </div>
    </div>
  );
}
