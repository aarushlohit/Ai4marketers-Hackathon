/** Core shared TypeScript types for Miracle Birds frontend. */

export interface Customer {
  id: string;
  tenant_id: string;
  external_id: string | null;
  crm_source:
    "salesforce" | "zoho" | "hubspot" | "dynamics" | "pipedrive" | null;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  company: string | null;
  title: string | null;
  status: "active" | "inactive" | "churned";
  health_score: number | null;
  churn_probability: number | null;
  lead_score: number | null;
  lifetime_value: number | null;
  created_at: string;
  updated_at: string;
}

export interface ChurnPrediction {
  customer_id: string;
  churn_probability: number;
  risk_level: "low" | "medium" | "high";
  factors: { name: string; impact: number }[];
  predicted_churn_date: string | null;
  confidence: number;
}

export interface LeadScore {
  customer_id: string;
  score: number;
  grade: "A" | "B" | "C" | "D" | "F";
  factors: { name: string; score: number }[];
}

export interface HealthScore {
  customer_id: string;
  score: number;
  status: "excellent" | "good" | "fair" | "poor" | "critical";
  factors: Record<string, number>;
  trend: "improving" | "stable" | "declining";
  calculated_at: string;
}

export interface CRMConnection {
  id: string;
  crm_type: "salesforce" | "zoho" | "hubspot" | "dynamics" | "pipedrive";
  status: "active" | "inactive" | "error";
  instance_url: string | null;
  last_sync: string | null;
  created_at: string;
}

export interface SyncJob {
  job_id: string;
  connection_id: string;
  sync_type: "full" | "incremental";
  status: "pending" | "running" | "completed" | "failed";
  started_at: string;
  records_synced: number | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export type UserRole = "super_admin" | "admin" | "manager" | "user" | "viewer";
