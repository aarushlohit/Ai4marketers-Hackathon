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
      <label className="mb-1.5 block text-sm font-medium text-slate-700">
        {label}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}

const inputCls =
  "w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm transition-colors placeholder:text-slate-400 focus:border-sky-500 focus:outline-none focus:ring-4 focus:ring-sky-100";

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
    <div className="min-h-screen bg-[#fbfdff] text-slate-950 lg:flex">
      {/* LEFT PANEL */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-[#f1f9ff] p-12 lg:flex">
        <div className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full bg-sky-200/60 blur-3xl" />
        <div>
          <div className="relative flex items-center gap-3 text-3xl font-semibold tracking-[-0.05em] text-slate-950">
            <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-sky-500 text-xl shadow-lg shadow-sky-200">🐦</span> Miracle Birds
          </div>
          <p className="relative mb-12 mt-5 max-w-sm text-xl font-medium leading-8 text-slate-600">
            Build a clearer, more connected customer workflow.
          </p>

          <div className="relative space-y-6 text-base text-slate-600">
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-sky-600 text-sm shadow-sm">✓</span>
              Start turning your CRM data into revenue in minutes
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-sky-600 text-sm shadow-sm">✓</span>
              14-day free trial · No credit card required
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
      <div className="flex w-full flex-col justify-center overflow-y-auto px-6 py-12 sm:px-16 lg:w-1/2 lg:border-l lg:border-slate-200 lg:px-24">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-[-0.05em] text-slate-950">
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
              <p className="text-sm text-red-600">
                Registration failed. Please try again.
              </p>
            )}

            <button
              type="submit"
              disabled={isPending}
              className="mt-4 w-full rounded-xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-100 transition-colors hover:bg-sky-600 disabled:opacity-50"
            >
              {isPending ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-sky-600 hover:text-sky-700 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
