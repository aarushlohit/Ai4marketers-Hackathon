"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth.store";
import Link from "next/link";

const schema = z
  .object({
    first_name: z.string().min(1, "Required"),
    last_name: z.string().min(1, "Required"),
    email: z.string().email("Enter a valid email"),
    company_name: z.string().min(1, "Required"),
    password: z.string().min(8, "Minimum 8 characters"),
    confirm_password: z.string(),
  })
  .refine((d) => d.password === d.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
  });

type RegisterForm = z.infer<typeof schema>;

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
        {label}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}

const inputCls =
  "w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm transition-colors focus:border-neutral-900 focus:outline-none focus:ring-1 focus:ring-neutral-900 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:focus:border-white dark:focus:ring-white";

export default function RegisterPage() {
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({ resolver: zodResolver(schema) });

  const { mutate, isPending, error } = useMutation({
    mutationFn: (data: RegisterForm) =>
      apiClient.post("/auth/register", data).then((r) => r.data),
    onSuccess: async (user) => {
      // Auto-login after registration
      const tokens = await apiClient
        .post("/auth/login", {
          email: user.email,
          password: (document.getElementById("pw") as HTMLInputElement)?.value,
        })
        .then((r) => r.data)
        .catch(() => null);

      if (tokens) {
        setTokens(tokens.access_token, tokens.refresh_token);
        setUser({
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role,
          tenantId: user.tenant_id,
        });
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
            Join Miracle Birds
          </p>

          <div className="space-y-6 text-lg text-neutral-400">
            <div className="flex items-center gap-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-white text-sm">✓</span>
              Start turning your CRM data into revenue in minutes
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-white text-sm">✓</span>
              14-day free trial · No credit card required
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
      <div className="flex w-full lg:w-1/2 flex-col justify-center px-8 sm:px-16 lg:px-24 py-12 bg-white dark:bg-dark-surface dark:border-l dark:border-dark-border overflow-y-auto">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 dark:text-white tracking-tight">
              Create your account
            </h1>
          </div>

          <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <Field label="First name" error={errors.first_name?.message}>
                <input
                  {...register("first_name")}
                  className={inputCls}
                  placeholder="Jane"
                />
              </Field>
              <Field label="Last name" error={errors.last_name?.message}>
                <input
                  {...register("last_name")}
                  className={inputCls}
                  placeholder="Doe"
                />
              </Field>
            </div>

            <Field label="Work email" error={errors.email?.message}>
              <input
                {...register("email")}
                type="email"
                className={inputCls}
                placeholder="jane@company.com"
              />
            </Field>

            <Field label="Company name" error={errors.company_name?.message}>
              <input
                {...register("company_name")}
                className={inputCls}
                placeholder="Acme Corp"
              />
            </Field>

            <Field label="Password" error={errors.password?.message}>
              <input
                id="pw"
                {...register("password")}
                type="password"
                className={inputCls}
                placeholder="••••••••"
              />
            </Field>

            <Field
              label="Confirm password"
              error={errors.confirm_password?.message}
            >
              <input
                {...register("confirm_password")}
                type="password"
                className={inputCls}
                placeholder="••••••••"
              />
            </Field>

            {error && (
              <p className="text-sm text-red-600 dark:text-red-400">
                Registration failed. Please try again.
              </p>
            )}

            <button
              type="submit"
              disabled={isPending}
              className="mt-4 w-full rounded-xl bg-black px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-neutral-800 disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-neutral-200"
            >
              {isPending ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-neutral-600 dark:text-neutral-400">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-black hover:underline dark:text-white">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
