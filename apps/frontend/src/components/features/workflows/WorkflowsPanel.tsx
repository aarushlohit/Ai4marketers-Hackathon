"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Play,
  Pause,
  Trash2,
  Plus,
  Zap,
  ArrowRight,
  Save,
  X,
  Mail,
  MessageSquare,
  UserPlus,
} from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface Workflow {
  id: string;
  name: string;
  description: string | null;
  conditions: any;
  actions: any[];
  is_active: boolean;
}

const TRIGGER_LABELS: Record<string, string> = {
  churn_risk_high: "Churn risk exceeds threshold (> 50%)",
  lead_score_changed: "Lead score changes significantly",
  health_score_drop: "Health score drops below 50",
  scheduled: "Scheduled (cron)",
};

const WORKFLOW_TEMPLATES = [
  {
    name: "Churn Risk Alert",
    description: "Notify team and send retention email when customer churn risk exceeds 70%",
    trigger: "churn_risk_high",
    actions: [
      { type: "send_email", config: { to: "{{email}}", subject: "We miss you!", body: "Dear {{name}}, we noticed your engagement has dropped..." } },
      { type: "notify_slack", config: { channel: "#customer-success", message: "⚠️ High churn risk: {{name}}" } },
    ],
    icon: "🚨",
  },
  {
    name: "Health Drop Rescue",
    description: "Auto-assign CSM and send check-in when health score drops below 50",
    trigger: "health_score_drop",
    actions: [
      { type: "assign_team", config: { team_id: "retention-team" } },
      { type: "send_email", config: { to: "{{email}}", subject: "How can we help?", body: "Hi {{name}}, we want to make sure you are getting value..." } },
    ],
    icon: "🏥",
  },
  {
    name: "Upsell Opportunity",
    description: "Assign sales rep and send proposal when lead score exceeds 80",
    trigger: "lead_score_changed",
    actions: [
      { type: "assign_team", config: { team_id: "sales-team" } },
      { type: "send_email", config: { to: "{{email}}", subject: "Exclusive upgrade for you", body: "Hi {{name}}, based on your usage we think you'd love our Pro plan..." } },
    ],
    icon: "📈",
  },
  {
    name: "Onboarding Welcome",
    description: "Send welcome email and assign onboarding team for new customers",
    trigger: "lead_score_changed",
    actions: [
      { type: "send_email", config: { to: "{{email}}", subject: "Welcome to the platform!", body: "Hi {{name}}, welcome! Here is how to get started..." } },
      { type: "assign_team", config: { team_id: "onboarding-team" } },
      { type: "notify_slack", config: { channel: "#onboarding", message: "🎉 New customer: {{name}}" } },
    ],
    icon: "🎉",
  },
  {
    name: "Renewal Reminder",
    description: "Notify customer and CSM team 30 days before contract renewal",
    trigger: "scheduled",
    actions: [
      { type: "send_email", config: { to: "{{email}}", subject: "Your renewal is coming up", body: "Hi {{name}}, your subscription renews in 30 days..." } },
      { type: "notify_slack", config: { channel: "#renewals", message: "📅 Renewal due: {{name}}" } },
    ],
    icon: "🔄",
  },
  {
    name: "Support Escalation",
    description: "Escalate to senior team and notify manager when customer sends critical support request",
    trigger: "health_score_drop",
    actions: [
      { type: "assign_team", config: { team_id: "senior-support" } },
      { type: "notify_slack", config: { channel: "#escalations", message: "🔴 Critical escalation: {{name}}" } },
    ],
    icon: "🆘",
  },
] as const;


export function WorkflowsPanel() {
  const qc = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [triggerType, setTriggerType] = useState("health_score_drop");
  const [actions, setActions] = useState<any[]>([]);

  const { data, isLoading } = useQuery({
    queryKey: ["workflows"],
    queryFn: () => apiClient.get("/workflows").then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (newWf: any) =>
      apiClient.post("/workflows", newWf).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workflows"] });
      setIsCreating(false);
      setName("");
      setDescription("");
      setActions([]);
    },
  });

  const toggleMutation = useMutation({
    mutationFn: (id: string) =>
      apiClient.put(`/workflows/${id}/toggle`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workflows"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.delete(`/workflows/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["workflows"] }),
  });

  const workflows: Workflow[] = Array.isArray(data) ? data : [];

  const handleAddAction = (type: string) => {
    let newAction = {};
    if (type === "send_email") {
      newAction = {
        type,
        config: {
          to: "{{email}}",
          subject: "Review Required",
          body: "Dear Manager...",
        },
      };
    } else if (type === "notify_slack") {
      newAction = {
        type,
        config: { channel: "#alerts", message: "Customer health critical!" },
      };
    } else if (type === "assign_team") {
      newAction = { type, config: { team_id: "retention-team" } };
    }
    setActions([...actions, newAction]);
  };

  const handleRemoveAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const handleSave = () => {
    if (!name) return;

    let conditions = {};
    if (triggerType === "health_score_drop") {
      conditions = { field: "health_score", operator: "lt", value: 50 };
    } else if (triggerType === "churn_risk_high") {
      conditions = { field: "churn_probability", operator: "gt", value: 0.5 };
    }

    createMutation.mutate({
      name,
      description,
      conditions,
      actions,
      is_active: true,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-bold text-slate-800 dark:text-white">Active CRM Rules</h2>
        {!isCreating && (
          <button
            onClick={() => setIsCreating(true)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            New Visual Workflow
          </button>
        )}
      </div>

      {/* Template Gallery */}
      {!isCreating && (
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-dark-muted">Quick Templates</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
            {WORKFLOW_TEMPLATES.map((tpl) => (
              <div
                key={tpl.name}
                className="rounded-2xl border border-slate-200 bg-white p-4 space-y-3 hover:shadow-md transition-shadow dark:border-dark-border dark:bg-dark-surface hover:dark:bg-dark-bg/70"
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl">{tpl.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-slate-800 dark:text-white">{tpl.name}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-snug">{tpl.description}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <div className="flex flex-wrap gap-1">
                    {tpl.actions.map((a, i) => (
                      <span key={i} className="rounded-md bg-slate-100 dark:bg-dark-bg/60 border border-slate-200 dark:border-dark-border px-1.5 py-0.5 text-[10px] font-semibold text-slate-600 dark:text-slate-400 capitalize">
                        {a.type.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                  <button
                    onClick={() => {
                      setName(tpl.name);
                      setDescription(tpl.description);
                      setTriggerType(tpl.trigger);
                      setActions([...tpl.actions]);
                      setIsCreating(true);
                    }}
                    className="ml-2 shrink-0 rounded-lg bg-slate-900 dark:bg-white px-3 py-1.5 text-xs font-semibold text-white dark:text-slate-900 hover:bg-slate-700 dark:hover:bg-slate-100 transition"
                  >
                    Use
                  </button>
                </div>
              </div>
            ))}

          </div>
        </div>
      )}

      {isCreating && (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-6 dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
          <div className="flex items-center justify-between border-b pb-4 dark:border-dark-border">
            <h3 className="font-bold text-slate-800 dark:text-white">
              CRM Visual Workflow Builder
            </h3>
            <button
              onClick={() => setIsCreating(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Workflow Name
              </label>
              <input
                type="text"
                placeholder="APAC Retention Pipeline"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-slate-200 p-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg/30 dark:text-white"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
                Description
              </label>
              <input
                type="text"
                placeholder="Automated actions for customers requiring engagement"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full rounded-lg border border-slate-200 p-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg/30 dark:text-white"
              />
            </div>
          </div>

          {/* Trigger Node */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
              Step 1: Define Trigger
            </span>
            <div className="rounded-xl border border-blue-200 bg-blue-50/50 p-4 dark:border-blue-900/30 dark:bg-blue-950/20">
              <div className="flex items-center gap-3">
                <Zap className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                    IF Customer Event Occurs
                  </p>
                  <select
                    value={triggerType}
                    onChange={(e) => setTriggerType(e.target.value)}
                    className="mt-1.5 rounded border border-blue-300 bg-white p-1.5 text-xs text-blue-900 focus:outline-none dark:border-blue-900 dark:bg-dark-bg dark:text-blue-300"
                  >
                    <option value="health_score_drop">
                      Health score drops below 50
                    </option>
                    <option value="churn_risk_high">
                      Churn probability exceeds 50%
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Connection Line */}
          <div className="flex justify-center">
            <ArrowRight className="h-6 w-6 rotate-90 text-slate-300 dark:text-dark-border" />
          </div>

          {/* Action Nodes */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-green-600 dark:text-green-400">
                Step 2: Executable Actions
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleAddAction("send_email")}
                  className="flex items-center gap-1 rounded-lg bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700 border border-green-200 hover:bg-green-100 dark:bg-green-950/20 dark:border-green-900/30 dark:text-green-400"
                >
                  <Mail className="h-3.5 w-3.5" /> + Email
                </button>
                <button
                  onClick={() => handleAddAction("notify_slack")}
                  className="flex items-center gap-1 rounded-lg bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700 border border-green-200 hover:bg-green-100 dark:bg-green-950/20 dark:border-green-900/30 dark:text-green-400"
                >
                  <MessageSquare className="h-3.5 w-3.5" /> + Slack
                </button>
                <button
                  onClick={() => handleAddAction("assign_team")}
                  className="flex items-center gap-1 rounded-lg bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700 border border-green-200 hover:bg-green-100 dark:bg-green-950/20 dark:border-green-900/30 dark:text-green-400"
                >
                  <UserPlus className="h-3.5 w-3.5" /> + Team
                </button>
              </div>
            </div>

            {actions.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-xs text-slate-500 dark:border-dark-border dark:text-dark-muted">
                No actions configured. Click above to add steps to this workflow.
              </div>
            ) : (
              <div className="space-y-3">
                {actions.map((action, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between rounded-xl border border-green-200 bg-green-50/30 p-4 dark:border-green-900/30 dark:bg-green-950/10"
                  >
                    <div className="flex items-center gap-3">
                      {action.type === "send_email" && (
                        <Mail className="h-5 w-5 text-green-600 dark:text-green-400" />
                      )}
                      {action.type === "notify_slack" && (
                        <MessageSquare className="h-5 w-5 text-green-600 dark:text-green-400" />
                      )}
                      {action.type === "assign_team" && (
                        <UserPlus className="h-5 w-5 text-green-600 dark:text-green-400" />
                      )}
                      <div>
                        <p className="text-sm font-semibold text-green-950 dark:text-green-300 capitalize">
                          {action.type.replace("_", " ")}
                        </p>
                        <p className="text-xs text-green-700/70 dark:text-green-400/60">
                          {action.type === "send_email" &&
                            `To: ${action.config.to} | Subject: ${action.config.subject}`}
                          {action.type === "notify_slack" &&
                            `Channel: ${action.config.channel} | Message: ${action.config.message}`}
                          {action.type === "assign_team" &&
                            `Assign to: ${action.config.team_id}`}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemoveAction(index)}
                      className="text-rose-400 hover:text-rose-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 border-t pt-4 dark:border-dark-border">
            <button
              onClick={() => setIsCreating(false)}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 dark:border-dark-border dark:text-slate-300 dark:hover:bg-dark-surface"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!name || actions.length === 0}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              Save Workflow
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-dark-surface"
            />
          ))}
        </div>
      ) : workflows.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-slate-200 bg-white py-16 text-center dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl">
          <Zap className="h-10 w-10 text-slate-300 dark:text-dark-muted animate-pulse" />
          <div>
            <p className="font-bold text-slate-700 dark:text-white">
              No workflows configured yet
            </p>
            <p className="text-sm text-slate-400 dark:text-dark-muted mt-1">
              Build your first adaptive CRM workflow rules using the builder above.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {workflows.map((wf) => (
            <div
              key={wf.id}
              className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-dark-border dark:bg-dark-bg/50 dark:backdrop-blur-xl"
            >
              <div className="flex items-start gap-3">
                <Zap className="mt-0.5 h-5 w-5 flex-shrink-0 text-blue-500 dark:text-blue-400" />
                <div>
                  <p className="text-sm font-bold text-slate-800 dark:text-white">{wf.name}</p>
                  <p className="text-xs text-slate-500 dark:text-dark-muted mt-0.5">
                    IF {wf.conditions?.field?.replace("_", " ")}{" "}
                    {wf.conditions?.operator === "lt" ? "<" : ">"}{" "}
                    {wf.conditions?.value}
                  </p>
                  {wf.description && (
                    <p className="mt-0.5 text-xs text-slate-400 dark:text-dark-muted">
                      {wf.description}
                    </p>
                  )}
                  <div className="mt-2 flex gap-1.5">
                    {wf.actions.map((act, index) => (
                      <span
                        key={index}
                        className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600 capitalize dark:bg-dark-surface dark:text-dark-muted"
                      >
                        {act.type.replace("_", " ")}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    wf.is_active
                      ? "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400"
                      : "bg-slate-100 text-slate-500 dark:bg-dark-surface dark:text-dark-muted"
                  }`}
                >
                  {wf.is_active ? "Active" : "Paused"}
                </span>
                <button
                  onClick={() => toggleMutation.mutate(wf.id)}
                  className="rounded-lg border border-slate-200 p-1.5 hover:bg-slate-50 dark:border-dark-border dark:hover:bg-dark-surface dark:text-dark-muted"
                  title={wf.is_active ? "Pause" : "Activate"}
                >
                  {wf.is_active ? (
                    <Pause className="h-4 w-4 text-slate-500 dark:text-dark-muted" />
                  ) : (
                    <Play className="h-4 w-4 text-slate-500 dark:text-dark-muted" />
                  )}
                </button>
                <button
                  onClick={() => deleteMutation.mutate(wf.id)}
                  className="rounded-lg border border-slate-200 p-1.5 hover:bg-rose-50 dark:border-dark-border dark:hover:bg-rose-950/20"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4 text-rose-400" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
