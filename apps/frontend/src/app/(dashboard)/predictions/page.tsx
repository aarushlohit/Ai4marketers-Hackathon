import { PredictionsDashboard } from "@/components/features/predictions/PredictionsDashboard";

export default function PredictionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Predictions</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          AI-powered predictions for churn risk, lead scoring, and revenue
          forecasting
        </p>
      </div>
      <PredictionsDashboard />
    </div>
  );
}
