"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { useAuthStore } from "@/stores/auth.store";

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
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>
      <div className="mt-1">{children}</div>
      {error && <p className="mt-1 text-xs text-red-500">{error}</p>}
    </div>
  );
}

const inputCls =
  "w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-dark-border dark:bg-dark-bg dark:text-white dark:placeholder-dark-muted";

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
    <div className="flex min-h-screen items-center justify-center bg-gray-50 py-12 dark:bg-dark-bg">
      <div className="w-full max-w-md space-y-8 rounded-xl bg-white p-8 shadow-lg dark:bg-dark-surface dark:border dark:border-dark-border">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🐦 Miracle Birds</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Create your account</p>
        </div>

        <form onSubmit={handleSubmit((d) => mutate(d))} className="space-y-4">
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
            className="w-full rounded-md bg-dark-accent px-4 py-2 text-sm font-semibold text-white hover:bg-dark-accent/90 disabled:opacity-50"
          >
            {isPending ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          Already have an account?{" "}
          <a href="/login" className="text-blue-600 hover:underline dark:text-blue-400">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}
