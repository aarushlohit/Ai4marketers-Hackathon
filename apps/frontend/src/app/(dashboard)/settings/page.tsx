import { SettingsPanel } from "@/components/features/settings/SettingsPanel";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Manage your account and organization preferences
        </p>
      </div>
      <SettingsPanel />
    </div>
  );
}
