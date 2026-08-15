"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth.store";
import Link from "next/link";

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
    <div className="flex min-h-screen bg-white dark:bg-dark-bg">
      {/* LEFT PANEL */}
      <div className="hidden lg:flex w-1/2 flex-col justify-between p-12 bg-gradient-to-br from-[#0a0a0a] to-[#1a1a1a] text-white">
        <div>
          <div className="text-4xl font-bold mb-4 flex items-center gap-2">
            <span>🐦</span> Miracle Birds
          </div>
          <p className="text-xl text-neutral-300 mb-12 font-medium">
            AI Intelligence Layer for CRM
          </p>

          <div className="space-y-6 text-lg text-neutral-400">
            <div className="flex items-center gap-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-white text-sm">✓</span>
              Predict churn before it happens
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-white text-sm">✓</span>
              Score and prioritize leads with AI
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-white text-sm">✓</span>
              Automate retention workflows
            </div>
          </div>
        </div>

        <div className="flex gap-4 text-sm font-medium text-neutral-500">
          <div className="flex items-center gap-1 rounded-full bg-white/5 px-3 py-1 border border-white/10">
            🔒 SOC 2
          </div>
          <div className="flex items-center gap-1 rounded-full bg-white/5 px-3 py-1 border border-white/10">
            🛡️ OWASP
          </div>
          <div className="flex items-center gap-1 rounded-full bg-white/5 px-3 py-1 border border-white/10">
            🔐 AES-256
          </div>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex w-full lg:w-1/2 flex-col justify-center px-8 sm:px-16 lg:px-24 bg-white dark:bg-dark-surface dark:border-l dark:border-dark-border">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 dark:text-white tracking-tight">
              Welcome back
            </h1>
            <p className="mt-2 text-neutral-500 dark:text-neutral-400">
              Sign in to your workspace
            </p>
          </div>

          <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-5">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Email
              </label>
              <input
                {...register("email")}
                type="email"
                className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm transition-colors focus:border-neutral-900 focus:outline-none focus:ring-1 focus:ring-neutral-900 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:focus:border-white dark:focus:ring-white"
                placeholder="you@company.com"
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Password
              </label>
              <input
                {...register("password")}
                type="password"
                className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm transition-colors focus:border-neutral-900 focus:outline-none focus:ring-1 focus:ring-neutral-900 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:focus:border-white dark:focus:ring-white"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
              )}
            </div>

            {mfaRequired && (
              <div>
                <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
                  MFA Code
                </label>
                <input
                  {...register("mfa_code")}
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm transition-colors focus:border-neutral-900 focus:outline-none focus:ring-1 focus:ring-neutral-900 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:focus:border-white dark:focus:ring-white"
                  placeholder="6-digit code"
                />
              </div>
            )}

            {error && (
              <p className="text-sm text-red-600 dark:text-red-400">
                Invalid email or password. Please try again.
              </p>
            )}

            <button
              type="submit"
              disabled={isPending}
              className="mt-2 w-full rounded-xl bg-black px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-neutral-800 disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-neutral-200"
            >
              {isPending ? "Signing in…" : mfaRequired ? "Verify & Sign in" : "Sign in"}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-neutral-600 dark:text-neutral-400">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="font-semibold text-black hover:underline dark:text-white">
              Sign up
            </Link>
          </p>

          <p className="mt-12 text-center text-xs text-neutral-400 dark:text-neutral-500">
            By signing in you agree to our Terms of Service
          </p>
        </div>
      </div>
    </div>
  );
}
