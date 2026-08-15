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
    <div className="min-h-screen bg-[#fbfdff] text-slate-950 lg:flex">
      {/* LEFT PANEL */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-[#f1f9ff] p-12 lg:flex">
        <div className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-sky-200/60 blur-3xl" />
        <div>
          <div className="relative flex items-center gap-3 text-3xl font-semibold tracking-[-0.05em] text-slate-950">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-sky-500 text-xl shadow-lg shadow-sky-200">🐦</span> Miracle Birds
          </div>
          <p className="relative mb-12 mt-5 max-w-sm text-xl font-medium leading-8 text-slate-600">
            A clearer way to turn customer intelligence into momentum.
          </p>

          <div className="relative space-y-6 text-base text-slate-600">
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-sky-600 text-sm shadow-sm">✓</span>
              Predict churn before it happens
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-sky-600 text-sm shadow-sm">✓</span>
              Score and prioritize leads with AI
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-sky-600 text-sm shadow-sm">✓</span>
              Automate retention workflows
            </div>
          </div>
        </div>

        <div className="relative flex gap-3 text-xs font-semibold text-slate-500">
          <div className="rounded-full border border-sky-200 bg-white px-3 py-1.5">SOC 2</div>
          <div className="rounded-full border border-sky-200 bg-white px-3 py-1.5">OWASP</div>
          <div className="rounded-full border border-sky-200 bg-white px-3 py-1.5">AES-256</div>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex w-full flex-col justify-center px-6 py-12 sm:px-16 lg:w-1/2 lg:border-l lg:border-slate-200 lg:px-24">
        <div className="mx-auto w-full max-w-sm">
          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-[-0.05em] text-slate-950">
              Welcome back
            </h1>
            <p className="mt-2 text-slate-500">
              Sign in to your workspace
            </p>
          </div>

          <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-5">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                Email
              </label>
              <input
                {...register("email")}
                type="email"
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm transition-colors placeholder:text-slate-400 focus:border-sky-500 focus:outline-none focus:ring-4 focus:ring-sky-100"
                placeholder="you@company.com"
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-700">
                Password
              </label>
              <input
                {...register("password")}
                type="password"
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm transition-colors placeholder:text-slate-400 focus:border-sky-500 focus:outline-none focus:ring-4 focus:ring-sky-100"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
              )}
            </div>

            {mfaRequired && (
              <div>
                <label className="mb-1.5 block text-sm font-medium text-slate-700">
                  MFA Code
                </label>
                <input
                  {...register("mfa_code")}
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm transition-colors placeholder:text-slate-400 focus:border-sky-500 focus:outline-none focus:ring-4 focus:ring-sky-100"
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
              className="mt-2 w-full rounded-xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-100 transition-colors hover:bg-sky-600 disabled:opacity-50"
            >
              {isPending ? "Signing in…" : mfaRequired ? "Verify & Sign in" : "Sign in"}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-500">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="font-semibold text-sky-600 hover:text-sky-700 hover:underline">
              Sign up
            </Link>
          </p>

          <p className="mt-12 text-center text-xs text-slate-400">
            By signing in you agree to our Terms of Service
          </p>
        </div>
      </div>
    </div>
  );
}
