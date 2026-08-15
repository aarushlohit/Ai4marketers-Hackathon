import { WorkflowsPanel } from "@/components/features/workflows/WorkflowsPanel";

export default function WorkflowsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Workflows</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Automate actions triggered by AI predictions and customer events
        </p>
      </div>
      <WorkflowsPanel />
    </div>
  );
}
