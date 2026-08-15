"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth.store";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  mfa_code: z.string().optional(),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();
  const [mfaRequired, setMfaRequired] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const { mutate, isPending, error } = useMutation({
    mutationFn: (data: LoginForm) =>
      apiClient.post("/auth/login", data).then((r) => r.data),
    onSuccess: async (data) => {
      if (data.mfa_required) {
        setMfaRequired(true);
        return;
      }
      setTokens(data.access_token, data.refresh_token);
      
      // Fetch user profile immediately to store in Zustand
      try {
        const userProfile = await apiClient.get("/users/me").then((r) => r.data);
        setUser({
          id: userProfile.id,
          email: userProfile.email,
          firstName: userProfile.first_name,
          lastName: userProfile.last_name,
          role: userProfile.role,
          tenantId: userProfile.tenant_id,
          mfaEnabled: userProfile.mfa_enabled,
        });
      } catch (err) {
        console.error("Failed to fetch user profile:", err);
      }
      
      router.push("/overview");
    },
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-dark-bg">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-lg dark:bg-dark-surface dark:border dark:border-dark-border">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Miracle Birds</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            AI Intelligence Layer for CRM
          </p>
        </div>

        <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Email
            </label>
            <input
              {...register("email")}
              type="email"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:placeholder-dark-muted"
              placeholder="you@company.com"
            />
            {errors.email && (
              <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Password
            </label>
            <input
              {...register("password")}
              type="password"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:placeholder-dark-muted"
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
            )}
          </div>

          {mfaRequired && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                MFA Code
              </label>
              <input
                {...register("mfa_code")}
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-bg dark:text-white"
                placeholder="6-digit code"
              />
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600">
              Invalid email or password. Please try again.
            </p>
          )}

          <button
            type="submit"
            disabled={isPending}
            className="w-full rounded-md bg-dark-accent px-4 py-2 text-sm font-semibold text-white hover:bg-dark-accent/90 disabled:opacity-50"
          >
            {isPending ? "Signing in…" : mfaRequired ? "Verify & Sign in" : "Sign in"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          Don&apos;t have an account?{" "}
          <a href="/register" className="text-blue-600 hover:underline dark:text-blue-400">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
