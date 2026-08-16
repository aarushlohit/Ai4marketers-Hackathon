/**
 * Axios HTTP client with JWT auth interceptors and automatic token refresh.
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/stores/auth.store";

const isServer = typeof window === "undefined";
const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (isServer
    ? "http://backend:8000"
    : process.env.NODE_ENV === "production"
      ? "https://mb-backend-rnhn.onrender.com"
      : "");

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

// ── Request interceptor: attach Bearer token ──────────────────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor: refresh token on 401 ───────────────────────────────
let refreshing = false;
let waitQueue: Array<(token: string) => void> = [];

apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    const isAuthEndpoint = original.url?.includes("/auth/login") || original.url?.includes("/auth/refresh") || original.url?.includes("/auth/register");

    if (error.response?.status !== 401 || original._retry || isAuthEndpoint) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (refreshing) {
      return new Promise((resolve) => {
        waitQueue.push((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          resolve(apiClient(original));
        });
      });
    }

    refreshing = true;
    try {
      const refreshToken = useAuthStore.getState().refreshToken;
      const { data } = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
        refresh_token: refreshToken,
      });

      useAuthStore.getState().setTokens(data.access_token, data.refresh_token);
      waitQueue.forEach((cb) => cb(data.access_token));
      waitQueue = [];
      original.headers.Authorization = `Bearer ${data.access_token}`;
      return apiClient(original);
    } catch {
      useAuthStore.getState().logout();
      window.location.href = "/login";
      return Promise.reject(error);
    } finally {
      refreshing = false;
    }
  },
);
