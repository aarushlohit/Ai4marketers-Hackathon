"use client";

import { useEffect, useState } from "react";
import { Bell, LogOut, ShieldAlert, Check } from "lucide-react";
import { useAuthStore } from "@/stores/auth.store";
import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { UserAvatar } from "@/components/ui/user-avatar";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

interface Threat {
  id: string;
  threat_type: string;
  severity: string;
  description: string;
  created_at: string;
}

export function DashboardNav() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [mounted, setMounted] = useState(false);

  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [hasUnread, setHasUnread] = useState(true);
  const [threats, setThreatsState] = useState<Threat[]>([]);

  const { data: fetchedThreats } = useQuery<Threat[]>({
    queryKey: ["threats"],
    queryFn: () => apiClient.get("/security/threats").then((r) => r.data),
    refetchInterval: 30000,
    enabled: mounted && !!user, // Only run query once client-side is mounted
  });

  useEffect(() => {
    if (fetchedThreats) {
      setThreatsState(fetchedThreats);
    }
  }, [fetchedThreats]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogout = () => {
    queryClient.clear();
    logout();
    router.push("/login");
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-dark-border dark:bg-dark-surface">
      <div className="flex items-center gap-2">
        <span className="text-sm text-slate-500 dark:text-dark-muted">
          AI Intelligence Layer for CRM
        </span>
      </div>

      <div className="flex items-center gap-4">
        <ThemeToggle />
        {/* Notifications Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setNotificationsOpen(!notificationsOpen);
              setHasUnread(false);
            }}
            className="relative rounded-full p-2 hover:bg-slate-100 dark:hover:bg-dark-surface"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5 text-slate-500 dark:text-dark-muted" />
            {hasUnread && threats.length > 0 && (
              <span className="absolute right-1 top-1 h-2.5 w-2.5 rounded-full bg-rose-500 ring-2 ring-white dark:ring-dark-surface animate-pulse" />
            )}
          </button>

          {notificationsOpen && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl border border-slate-200 bg-white p-4 shadow-xl dark:border-dark-border dark:bg-dark-surface z-50 space-y-3">
              <div className="flex items-center justify-between border-b pb-2 dark:border-dark-border">
                <span className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  <Bell className="h-4 w-4 text-blue-600" /> Notifications
                </span>
                {threats.length > 0 && (
                  <button
                    onClick={() => {
                      setThreatsState([]);
                      alert("Cleared all notifications!");
                    }}
                    className="text-xs font-semibold text-blue-600 hover:underline flex items-center gap-1"
                  >
                    <Check className="h-3 w-3" /> Clear All
                  </button>
                )}
              </div>

              <div className="max-h-64 overflow-y-auto space-y-2.5 pr-1">
                {threats.length === 0 ? (
                  <p className="text-xs text-slate-400 dark:text-dark-muted text-center py-6">
                    No new notifications
                  </p>
                ) : (
                  threats.map((t) => (
                    <div
                      key={t.id}
                      className="flex items-start gap-2.5 rounded-lg p-2 hover:bg-slate-50 dark:hover:bg-dark-bg/40 border border-transparent hover:border-slate-100 dark:hover:border-dark-border/40 transition"
                    >
                      <ShieldAlert
                        className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                          t.severity === "High"
                            ? "text-rose-500"
                            : t.severity === "Medium"
                              ? "text-amber-500"
                              : "text-blue-500"
                        }`}
                      />
                      <div className="space-y-0.5">
                        <p className="text-xs font-medium text-slate-800 dark:text-slate-200 leading-tight">
                          {t.description}
                        </p>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full uppercase ${
                              t.severity === "High"
                                ? "bg-rose-50 text-rose-600 dark:bg-rose-500/10 dark:text-rose-400"
                                : t.severity === "Medium"
                                  ? "bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400"
                                  : "bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400"
                            }`}
                          >
                            {t.severity}
                          </span>
                          <span className="text-[9px] text-slate-400 dark:text-dark-muted font-medium">
                            {new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <UserAvatar firstName={mounted ? user?.firstName : undefined} />
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-slate-900 dark:text-white">
              {mounted && user
                ? `${user.firstName} ${user.lastName}`
                : "User"}
            </p>
            <p className="text-xs capitalize text-slate-500 dark:text-dark-muted">
              {mounted && user?.role ? user.role : ""}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="rounded-full p-2 hover:bg-slate-100 dark:hover:bg-dark-surface"
          title="Sign out"
          aria-label="Sign out"
        >
          <LogOut className="h-5 w-5 text-slate-500 dark:text-dark-muted" />
        </button>
      </div>
    </header>
  );
}
