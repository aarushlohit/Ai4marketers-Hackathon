"use client";

import { memo } from "react";
import { cn, getFirstNameInitial } from "@/lib/utils";

interface UserAvatarProps {
  firstName?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZE_MAP = {
  sm: "h-7 w-7 text-xs",
  md: "h-8 w-8 text-sm",
  lg: "h-10 w-10 text-base",
} as const;

/**
 * Default account logo: first letter of the user's first name.
 */
export const UserAvatar = memo(function UserAvatar({
  firstName,
  size = "md",
  className,
}: UserAvatarProps) {
  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-full bg-blue-100 font-semibold text-blue-700 dark:bg-dark-accent/10 dark:text-dark-accent",
        SIZE_MAP[size],
        className,
      )}
      aria-hidden={!firstName}
      title={firstName || undefined}
    >
      {getFirstNameInitial(firstName)}
    </div>
  );
});
