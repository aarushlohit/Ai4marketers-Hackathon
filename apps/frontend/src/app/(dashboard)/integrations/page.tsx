import { IntegrationsPanel } from "@/components/features/integrations/IntegrationsPanel";

export default function IntegrationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Integrations</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Connect Miracle Birds to your existing CRM platforms
        </p>
      </div>
      <IntegrationsPanel />
    </div>
  );
}
