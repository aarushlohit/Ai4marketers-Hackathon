"use client";

import React, { useState, useEffect } from "react";
import { Layers } from "lucide-react";

const TEAM_MEMBERS = ["Ashlin Mirsha RK", "Lohit A", "Benesha Mercy Ramesh RA"];

export function CreatedBySection() {
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const maxLen = Math.max(...TEAM_MEMBERS.map((m) => m.length));

    if (isPaused) {
      const pauseTimer = setTimeout(() => {
        setIsPaused(false);
        setIsDeleting(true);
      }, 2500);
      return () => clearTimeout(pauseTimer);
    }

    const timer = setInterval(() => {
      setCharIndex((prev) => {
        if (!isDeleting) {
          if (prev >= maxLen) {
            setIsPaused(true);
            return maxLen;
          }
          return prev + 1;
        } else {
          if (prev <= 0) {
            setIsDeleting(false);
            return 0;
          }
          return prev - 1;
        }
      });
    }, isDeleting ? 40 : 90);

    return () => clearInterval(timer);
  }, [isDeleting, isPaused]);

  return (
    <section className="py-16 px-4 sm:px-6 lg:px-8 bg-[#f0f7ff] dark:bg-[#0d172a] text-center border border-sky-100/80 dark:border-slate-800/80 rounded-3xl my-8 transition-colors duration-300 shadow-sm">
      <div className="max-w-4xl mx-auto flex flex-col items-center">
        {/* Stack Icon */}
        <div className="w-12 h-12 rounded-2xl bg-white dark:bg-slate-900 border border-sky-100 dark:border-slate-800 shadow-sm flex items-center justify-center mb-5 text-sky-500">
          <Layers className="w-6 h-6" />
        </div>

        {/* Built with Purpose Label */}
        <p className="text-xs font-extrabold uppercase tracking-widest text-sky-500 mb-2">
          Built with purpose
        </p>

        {/* Main Heading */}
        <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-3">
          Created by Miracle Birds.
        </h2>

        {/* Subtitle */}
        <p className="text-slate-600 dark:text-slate-300 text-sm sm:text-base max-w-xl font-medium leading-relaxed mb-6">
          A focused team building a more human, useful intelligence layer for the people who care about customer relationships.
        </p>

        {/* Team Member Badges with Simultaneous Typewriter */}
        <div className="flex flex-wrap items-center justify-center gap-3">
          {TEAM_MEMBERS.map((name) => {
            const currentText = name.slice(0, charIndex);
            return (
              <div
                key={name}
                className="px-5 py-2.5 rounded-full bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-slate-800 dark:text-slate-100 font-semibold text-xs sm:text-sm shadow-sm flex items-center justify-center min-h-[42px] transition-all hover:shadow-md hover:border-sky-300"
              >
                <span>{currentText}</span>
                <span className="w-0.5 h-4 bg-sky-500 animate-pulse inline-block ml-0.5" />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
