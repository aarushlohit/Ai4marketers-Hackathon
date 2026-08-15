"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="h-9 w-9" />;
  }

  return (
    <button
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="relative rounded-full p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
      title="Toggle theme"
    >
      <Sun className="h-5 w-5 text-slate-500 transition-all scale-0 rotate-90 dark:rotate-0 dark:scale-100" />
      <Moon className="absolute left-1/2 top-1/2 h-5 w-5 -translate-x-1/2 -translate-y-1/2 text-slate-500 transition-all scale-100 rotate-0 dark:-rotate-90 dark:scale-0" />
    </button>
  );
}
