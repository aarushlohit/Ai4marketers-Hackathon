/** Customer API query functions for TanStack Query. */
import { apiClient } from "./client";
import type { Customer, PaginatedResponse } from "@/types";

export interface CustomerFilters {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  crm_source?: string;
}

export const customerApi = {
  list: (filters: CustomerFilters = {}) =>
    apiClient
      .get<{
        customers: Customer[];
        total: number;
        page: number;
        page_size: number;
      }>("/customers", { params: filters })
      .then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Customer>(`/customers/${id}`).then((r) => r.data),

  get360: (id: string) =>
    apiClient.get(`/customers/${id}/360`).then((r) => r.data),

  create: (data: Partial<Customer>) =>
    apiClient.post<Customer>("/customers", data).then((r) => r.data),

  update: (id: string, data: Partial<Customer>) =>
    apiClient.put<Customer>(`/customers/${id}`, data).then((r) => r.data),

  delete: (id: string) => apiClient.delete(`/customers/${id}`),
};

export const predictionsApi = {
  churn: (customerId: string) =>
    apiClient
      .post("/predictions/churn", { customer_id: customerId })
      .then((r) => r.data),

  leadScore: (customerId: string) =>
    apiClient
      .post("/predictions/lead-score", { customer_id: customerId })
      .then((r) => r.data),

  revenue: (customerId: string, timeHorizon = 90) =>
    apiClient
      .post("/predictions/revenue", {
        customer_id: customerId,
        time_horizon: timeHorizon,
      })
      .then((r) => r.data),

  healthScore: (customerId: string) =>
    apiClient
      .get(`/predictions/health-score/${customerId}`)
      .then((r) => r.data),
};
