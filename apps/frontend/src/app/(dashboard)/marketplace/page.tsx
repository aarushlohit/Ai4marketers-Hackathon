import { IntegrationsPanel } from "@/components/features/integrations/IntegrationsPanel";

export default function MarketplacePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Marketplace</h1>
        <p className="text-sm text-slate-500 dark:text-dark-muted mt-2">
          Discover and install extensions, CRM connectors, and AI models for your workspace.
        </p>
      </div>
      <IntegrationsPanel />
    </div>
  );
}
