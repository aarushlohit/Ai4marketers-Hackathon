"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Layers } from "lucide-react";


const TEAM_MEMBERS = ["Ashlin Mirsha RK", "Lohit A", "Benesha Mercy Ramesh RA"];

function CreatedBySection() {
  const [index, setIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const maxLen = Math.max(...TEAM_MEMBERS.map((m) => m.length));

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        if (index < maxLen) {
          setIndex((prev) => prev + 1);
        } else {
          // Pause at full text
          setTimeout(() => setIsDeleting(true), 2500);
        }
      } else {
        if (index > 0) {
          setIndex((prev) => prev - 1);
        } else {
          setIsDeleting(false);
        }
      }
    }, isDeleting ? 40 : 80);

    return () => clearTimeout(timeout);
  }, [index, isDeleting]);

  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#f0f7ff] dark:bg-[#0d172a] text-center border-t border-b border-sky-100/60 dark:border-slate-800 transition-colors duration-300">
      <div className="max-w-4xl mx-auto flex flex-col items-center">
        {/* Stack Icon */}
        <div className="w-12 h-12 rounded-2xl bg-white dark:bg-slate-900 border border-sky-100 dark:border-slate-800 shadow-sm flex items-center justify-center mb-6 text-sky-500">
          <Layers className="w-6 h-6" />
        </div>

        {/* Built with Purpose Label */}
        <p className="text-xs font-extrabold uppercase tracking-widest text-sky-500 mb-3">
          Built with purpose
        </p>

        {/* Main Heading */}
        <h2 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-4">
          Created by Miracle Birds.
        </h2>

        {/* Subtitle */}
        <p className="text-slate-600 dark:text-slate-300 text-base sm:text-lg max-w-2xl font-medium leading-relaxed mb-8">
          A focused team building a more human, useful intelligence layer for the people who care about customer relationships.
        </p>

        {/* Team Member Badges with Simultaneous Typewriter */}
        <div className="flex flex-wrap items-center justify-center gap-4">
          {TEAM_MEMBERS.map((name) => {
            const currentText = name.slice(0, index);
            return (
              <div
                key={name}
                className="px-6 py-3 rounded-full bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-slate-800 dark:text-slate-100 font-semibold text-sm sm:text-base shadow-sm flex items-center justify-center gap-1 min-w-[150px] transition-all hover:shadow-md hover:border-sky-300"
              >
                <span>{currentText}</span>
                <span className="w-0.5 h-4 bg-sky-500 animate-pulse inline-block" />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}


export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white selection:bg-green-500/30 font-sans dark:bg-[#0a0a0a] bg-slate-50 dark:text-white text-slate-900 transition-colors duration-300">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-500/10 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 border-b border-white/10 dark:border-white/10 border-slate-200 bg-white/5 dark:bg-white/5 bg-slate-900/5 backdrop-blur-md sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🐦</span>
            <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 dark:from-white dark:to-slate-400 from-slate-900 to-slate-600 bg-clip-text text-transparent">
              Miracle Birds
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-medium hover:text-slate-300 dark:hover:text-slate-300 text-slate-600 hover:text-slate-900 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="text-sm font-medium bg-white dark:bg-white bg-slate-900 text-black dark:text-black text-white px-4 py-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-200 hover:opacity-90 transition-all shadow-[0_0_15px_rgba(255,255,255,0.1)]"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10">
        {/* Hero Section */}
        <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-semibold uppercase tracking-wider mb-8">
            <span className="text-sm">🔒</span> Enterprise Security
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-tight">
            <span className="inline-block animate-gradient-text bg-gradient-to-r from-white via-slate-300 to-slate-500 dark:from-white dark:via-slate-300 dark:to-slate-500 from-slate-900 via-slate-700 to-slate-500 bg-clip-text text-transparent bg-[length:200%_auto]">
              The AI Intelligence Layer
            </span>
            <br />
            <span className="text-slate-400 dark:text-slate-400 text-slate-600">for Every CRM</span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 dark:text-slate-400 text-slate-600 max-w-3xl mx-auto mb-10 leading-relaxed">
            Connect your CRM, predict churn, score leads, and automate retention — all powered by AI, all secured by design.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            <Link
              href="/register"
              className="w-full sm:w-auto px-8 py-3 rounded-full bg-white dark:bg-white bg-slate-900 text-black dark:text-black text-white font-semibold hover:bg-slate-200 dark:hover:bg-slate-200 hover:opacity-90 transition-colors shadow-lg"
            >
              Start Free Trial &rarr;
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-3 rounded-full border border-white/20 dark:border-white/20 border-slate-300 font-semibold hover:bg-white/5 dark:hover:bg-white/5 hover:bg-slate-100 transition-colors"
            >
              View Demo
            </Link>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-slate-400 font-medium">
            <div className="flex items-center gap-2">
              <span className="text-lg">🔒</span> SOC 2 Compliant
            </div>
            <div className="hidden sm:block text-white/20">•</div>
            <div className="flex items-center gap-2">
              <span className="text-lg">🛡️</span> OWASP Top 10
            </div>
            <div className="hidden sm:block text-white/20">•</div>
            <div className="flex items-center gap-2">
              <span className="text-lg">🔐</span> AES-256 Encrypted
            </div>
          </div>
        </section>

        {/* Social Proof */}
        <section className="py-10 border-y border-white/10 dark:border-white/10 border-slate-200 bg-white/[0.02] dark:bg-white/[0.02] bg-slate-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p className="text-sm text-slate-500 font-medium uppercase tracking-widest mb-6">
              Trusted by leading revenue teams
            </p>
            <div className="flex flex-wrap justify-center gap-8 md:gap-16 items-center text-slate-500 dark:text-slate-500 text-slate-400 font-bold text-xl md:text-2xl grayscale opacity-70">
              <span>Acme Corp</span>
              <span>Globex</span>
              <span>Soylent</span>
              <span>Initech</span>
              <span>Stark Ind.</span>
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Supercharge your workflow</h2>
            <p className="text-slate-400">Everything you need to turn CRM data into revenue.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="p-6 rounded-2xl bg-white/5 dark:bg-white/5 bg-white border border-white/10 dark:border-white/10 border-slate-200 backdrop-blur-sm hover:border-white/20 dark:hover:border-white/20 hover:border-slate-300 transition-all group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">🧠</div>
              <h3 className="text-xl font-bold mb-2">AI Predictions</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Predict churn, score leads, forecast revenue with ML.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="p-6 rounded-2xl bg-white/5 dark:bg-white/5 bg-white border border-white/10 dark:border-white/10 border-slate-200 backdrop-blur-sm hover:border-white/20 dark:hover:border-white/20 hover:border-slate-300 transition-all group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">📊</div>
              <h3 className="text-xl font-bold mb-2">Customer 360</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Full profile: health score, deal history, activity timeline.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-6 rounded-2xl bg-white/5 dark:bg-white/5 bg-white border border-white/10 dark:border-white/10 border-slate-200 backdrop-blur-sm hover:border-white/20 dark:hover:border-white/20 hover:border-slate-300 transition-all group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">🔌</div>
              <h3 className="text-xl font-bold mb-2">CRM Connect</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Sync HubSpot, Salesforce, Zoho in one click.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="p-6 rounded-2xl bg-white/5 dark:bg-white/5 bg-white border border-white/10 dark:border-white/10 border-slate-200 backdrop-blur-sm hover:border-white/20 dark:hover:border-white/20 hover:border-slate-300 transition-all group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">🤖</div>
              <h3 className="text-xl font-bold mb-2">AI Copilot</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Ask questions about your CRM data in natural language.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="p-6 rounded-2xl bg-white/5 dark:bg-white/5 bg-white border border-white/10 dark:border-white/10 border-slate-200 backdrop-blur-sm hover:border-white/20 dark:hover:border-white/20 hover:border-slate-300 transition-all group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">🔄</div>
              <h3 className="text-xl font-bold mb-2">Workflows</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                Automate actions triggered by AI predictions.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="p-6 rounded-2xl bg-white/5 dark:bg-white/5 bg-white border border-white/10 dark:border-white/10 border-slate-200 backdrop-blur-sm hover:border-white/20 dark:hover:border-white/20 hover:border-slate-300 transition-all group">
              <div className="text-4xl mb-4 group-hover:scale-110 transition-transform origin-left">🔒</div>
              <h3 className="text-xl font-bold mb-2">Security</h3>
              <p className="text-slate-400 text-sm leading-relaxed">
                OWASP Top 10 compliant, E2E encrypted, audit logs.
              </p>
            </div>
          </div>
        </section>

        {/* Created by Miracle Birds Section with Simultaneous Typewriter */}
        <CreatedBySection />

        {/* CTA Footer */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden bg-gradient-to-b from-white/10 to-white/5 dark:from-white/10 dark:to-white/5 from-slate-200 to-slate-100 border border-white/10 dark:border-white/10 border-slate-300 p-12 text-center">
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjIiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz48L3N2Zz4=')] opacity-50 dark:opacity-50 opacity-20 mask-image:linear-gradient(to_bottom,white,transparent)]" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-5xl font-bold mb-6">
                Ready to stop guessing<br />and start growing?
              </h2>
              <Link
                href="/register"
                className="inline-block px-8 py-4 rounded-full bg-white dark:bg-white bg-slate-900 text-black dark:text-black text-white font-semibold hover:scale-105 transition-transform shadow-xl"
              >
                Get Started Free &rarr;
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 dark:border-white/10 border-slate-200 py-8 text-center relative z-10">
        <p className="text-slate-500 text-sm">
          &copy; 2026 Miracle Birds · AI Intelligence Layer for CRM · Built for Hackathon
        </p>
      </footer>

      {/* Global Styles for Animations */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes gradient-text {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .animate-gradient-text {
          animation: gradient-text 5s ease infinite;
        }
      `}} />
    </div>
  );
}
