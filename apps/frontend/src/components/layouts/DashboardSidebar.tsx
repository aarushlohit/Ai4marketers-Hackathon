"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Bot,
  Building2,
  GitBranch,
  LayoutDashboard,
  Settings,
  TrendingUp,
  Users,
  Video,
  FileText,
  DollarSign,
  ShoppingBag,
  Shield,
  Activity,
  UserCheck,
  Bird,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/overview", label: "Overview", icon: LayoutDashboard },
  { href: "/customers", label: "Customers", icon: Users },
  { href: "/predictions", label: "Predictions", icon: TrendingUp },
  { href: "/meetings", label: "Meetings", icon: Video },
  { href: "/executive", label: "Executive", icon: FileText },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/copilot", label: "AI Copilot", icon: Bot },
  { href: "/workflows", label: "Workflows", icon: GitBranch },
  { href: "/tenant-manager", label: "Tenant Manager", icon: UserCheck },
  { href: "/billing", label: "Billing", icon: DollarSign },
  { href: "/marketplace", label: "Marketplace", icon: ShoppingBag },
  { href: "/ai-governance", label: "AI Governance", icon: Activity },
  { href: "/security-center", label: "Security Center", icon: Shield },
  { href: "/settings", label: "Settings", icon: Settings },
];


export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 flex-col border-r border-slate-200 bg-white dark:border-dark-border dark:bg-dark-surface">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-slate-200 dark:border-dark-border px-6">
        <span className="flex items-center text-xl font-bold text-slate-900 dark:text-white">
          <Bird className="h-6 w-6 mr-2 text-sky-500 shrink-0" /> Miracle Birds
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-blue-50 text-blue-700 dark:bg-dark-accent/10 dark:text-dark-accent"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-dark-muted dark:hover:bg-dark-surface dark:hover:text-dark-accent",
              )}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-200 dark:border-dark-border p-4">
        <p className="text-xs text-gray-400">Miracle Birds v1.0</p>
      </div>
    </aside>
  );
}
