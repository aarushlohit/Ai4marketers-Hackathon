"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth.store";
import { apiClient } from "@/lib/api/client";
import { UserAvatar } from "@/components/ui/user-avatar";

import { Shield, CheckCircle, AlertTriangle } from "lucide-react";

const tabs = ["Profile", "Security", "Notifications"] as const;
type Tab = (typeof tabs)[number];

export function SettingsPanel() {
  const [activeTab, setActiveTab] = useState<Tab>("Profile");
  const [mounted, setMounted] = useState(false);
  const { user, setUser } = useAuthStore();

  const [showMfaModal, setShowMfaModal] = useState(false);
  const [mfaSecret, setMfaSecret] = useState("");
  const [qrCodeUrl, setQrCodeUrl] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaError, setMfaError] = useState("");

  const handleStartMfaSetup = async () => {
    try {
      const data = await apiClient.get("/security/mfa/setup").then((r) => r.data);
      setMfaSecret(data.mfa_secret);
      setQrCodeUrl(data.qr_code_placeholder);
      setMfaError("");
      setMfaCode("");
      setShowMfaModal(true);
    } catch (err: any) {
      alert("Failed to start MFA setup: " + err.message);
    }
  };

  const handleVerifyMfa = async () => {
    try {
      await apiClient.post("/security/mfa/verify", {
        mfa_secret: mfaSecret,
        code: mfaCode,
      });
      setUser({ ...user!, mfaEnabled: true });
      setShowMfaModal(false);
      alert("Two-Factor Authentication is now enabled!");
    } catch (err: any) {
      setMfaError(err.response?.data?.detail || "Invalid code. Please try again.");
    }
  };

  useEffect(() => {
    setMounted(true);
  }, []);

  const { register, handleSubmit } = useForm({
    defaultValues: {
      first_name: user?.firstName ?? "",
      last_name: user?.lastName ?? "",
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: object) =>
      apiClient.put("/users/me", data).then((r) => r.data),
  });

  const resetMutation = useMutation({
    mutationFn: () => apiClient.delete("/settings/reset-data"),
    onSuccess: () => window.alert("All CRM data and connected providers were reset."),
  });

  const handleReset = () => {
    if (window.confirm("Reset everything? This permanently deletes your CRM customers, meetings, workflows, recommendations, feedback, and all connected CRM providers. Your account will remain.")) {
      resetMutation.mutate();
    }
  };

  if (!mounted) return null;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-dark-border px-6">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-4 px-4 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab
                ? "border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-400"
                : "border-transparent text-slate-500 hover:text-slate-800 dark:text-dark-muted dark:hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="p-6">
        {activeTab === "Profile" && (
          <form
            onSubmit={handleSubmit((d) => updateMutation.mutate(d))}
            className="max-w-md space-y-4"
          >
            <div className="flex items-center gap-4 pb-2">
              <UserAvatar firstName={user?.firstName} size="lg" />
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-white">
                  {user?.firstName} {user?.lastName}
                </p>
                <p className="text-xs text-slate-500 dark:text-dark-muted">{user?.email}</p>
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
                Email
              </label>
              <input
                disabled
                value={user?.email ?? ""}
                className="mt-1 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500 dark:border-dark-border dark:bg-dark-bg/50 dark:text-dark-muted"
              />
            </div>

            <div className="rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-900/60 dark:bg-red-950/20">
              <div className="flex items-start gap-3">
                <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-red-800 dark:text-red-300">Reset all workspace data</p>
                  <p className="text-xs leading-5 text-red-700 dark:text-red-400">Permanently removes CRM records and disconnects every connected provider. Your login account remains.</p>
                  <button type="button" onClick={handleReset} disabled={resetMutation.isPending} className="rounded-lg bg-red-600 px-3 py-2 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50">
                    {resetMutation.isPending ? "Resetting…" : "Reset everything"}
                  </button>
                  {resetMutation.isError && <p className="text-xs text-red-700">Reset failed. Please try again.</p>}
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
                  First name
                </label>
                <input
                  {...register("first_name")}
                  className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg/30 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Last name
                </label>
                <input
                  {...register("last_name")}
                  className="mt-1 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg/30 dark:text-white"
                />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={updateMutation.isPending}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {updateMutation.isPending ? "Saving…" : "Save changes"}
              </button>
              {updateMutation.isSuccess && (
                <span className="text-sm text-green-600 dark:text-green-400">Saved!</span>
              )}
            </div>
          </form>
        )}

        {activeTab === "Security" && (
          <div className="max-w-md space-y-6">
            <div>
              <p className="text-sm text-slate-500 dark:text-dark-muted mb-4">
                Manage your password and two-factor authentication.
              </p>
              <button className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold hover:bg-slate-50 dark:border-dark-border dark:hover:bg-dark-surface dark:text-white">
                Change Password
              </button>
            </div>

            <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 dark:border-dark-border dark:bg-dark-bg/30">
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-white">
                  Two-Factor Authentication (2FA)
                </p>
                <p className="text-xs text-slate-500 dark:text-dark-muted mt-0.5">
                  Add an extra layer of security using a TOTP authenticator app (like Google Authenticator).
                </p>
              </div>
              {user?.mfaEnabled ? (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 px-2.5 py-1 rounded-full">
                  <CheckCircle className="h-3.5 w-3.5" />
                  Active
                </span>
              ) : (
                <button
                  onClick={handleStartMfaSetup}
                  className="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 transition"
                >
                  Enable
                </button>
              )}
            </div>

            {/* MFA Setup Modal */}
            {showMfaModal && (
              <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
                <div className="bg-white dark:bg-dark-surface dark:border dark:border-dark-border rounded-xl max-w-sm w-full p-6 shadow-xl space-y-4">
                  <div className="flex items-center gap-2 border-b pb-3 dark:border-dark-border">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <h3 className="text-lg font-bold text-slate-800 dark:text-white">Configure 2FA</h3>
                  </div>

                  <p className="text-xs text-slate-500 dark:text-dark-muted">
                    1. Scan the QR code below using your Authenticator App. If you cannot scan it, enter the code manually:
                  </p>

                  <div className="flex justify-center border p-3 rounded-lg dark:border-dark-border bg-white">
                    {qrCodeUrl ? (
                      <img src={qrCodeUrl} alt="MFA QR Code" className="h-44 w-44" />
                    ) : (
                      <div className="h-44 w-44 flex items-center justify-center bg-slate-50 text-slate-400">
                        Loading QR code...
                      </div>
                    )}
                  </div>

                  <div className="bg-slate-50 dark:bg-dark-bg p-2.5 rounded-lg border dark:border-dark-border text-center">
                    <code className="text-xs font-semibold text-slate-700 dark:text-slate-200 select-all">
                      {mfaSecret}
                    </code>
                  </div>

                  <div className="space-y-2">
                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300">
                      2. Enter the 6-digit confirmation code:
                    </label>
                    <input
                      type="text"
                      maxLength={6}
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ""))}
                      className="w-full text-center tracking-widest text-lg font-bold rounded-lg border py-2 dark:border-dark-border dark:bg-dark-bg dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="000000"
                    />
                    {mfaError && <p className="text-xs text-red-500 text-center">{mfaError}</p>}
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button
                      onClick={() => setShowMfaModal(false)}
                      className="flex-1 rounded-lg border py-2 text-sm font-semibold hover:bg-slate-50 dark:border-dark-border dark:text-white dark:hover:bg-dark-bg transition"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleVerifyMfa}
                      disabled={mfaCode.length !== 6}
                      className="flex-1 rounded-lg bg-blue-600 text-white py-2 text-sm font-semibold hover:bg-blue-700 transition disabled:opacity-50"
                    >
                      Verify & Activate
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "Notifications" && (
          <div className="max-w-md space-y-4">
            <p className="text-sm text-slate-500 dark:text-dark-muted">
              Configure when you receive email and in-app notifications.
            </p>
            {[
              "High churn risk alerts",
              "Lead score changes",
              "CRM sync failures",
              "Weekly AI summary",
            ].map((item) => (
              <label
                key={item}
                className="flex cursor-pointer items-center justify-between rounded-xl border border-slate-200 bg-white p-3 dark:border-dark-border dark:bg-dark-bg/30"
              >
                <span className="text-sm text-slate-700 dark:text-slate-300">{item}</span>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-slate-300 text-blue-600 dark:bg-dark-bg dark:border-dark-border"
                />
              </label>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
