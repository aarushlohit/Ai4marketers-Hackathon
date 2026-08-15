"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";

/**
 * Hook that guards authenticated routes.
 * Redirects to /login if the user has no valid token.
 */
export function useAuth({ required = true } = {}) {
  const router = useRouter();
  const { isAuthenticated, user, accessToken } = useAuthStore();

  useEffect(() => {
    if (required && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, required, router]);

  return { isAuthenticated, user, accessToken };
}
