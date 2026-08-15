"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Check,
  ChevronDown,
  CircleDollarSign,
  Layers3,
  Menu,
  ShieldCheck,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";

const features = [
  { icon: BrainCircuit, title: "Predict what matters", copy: "Spot churn risk, surface buying signals, and focus your team on the next best action." },
  { icon: Users, title: "See every customer clearly", copy: "Bring activity, deals, health, and context into one calm customer view." },
  { icon: Sparkles, title: "Turn insight into action", copy: "Let intelligent workflows move follow-ups forward while your team stays in control." },
];

const teamMembers = ["Ashlin Mirsha RK", "Lohit A", "Benesha Mercy Ramesh RA"];

function TeamTypewriter() {
  const [memberIndex, setMemberIndex] = useState(0);
  const [visibleLength, setVisibleLength] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const currentName = teamMembers[memberIndex];
    const finishedTyping = visibleLength === currentName.length;
    const finishedDeleting = deleting && visibleLength === 0;
    const delay = finishedTyping ? 1500 : deleting ? 55 : 90;

    const timer = window.setTimeout(() => {
      if (finishedDeleting) {
        setDeleting(false);
        setMemberIndex((index) => (index + 1) % teamMembers.length);
      } else if (finishedTyping) {
        setDeleting(true);
      } else {
        setVisibleLength((length) => length + (deleting ? -1 : 1));
      }
    }, delay);

    return () => window.clearTimeout(timer);
  }, [deleting, memberIndex, visibleLength]);

  return (
    <span className="inline-flex min-h-[1.15em] items-center font-mono text-4xl font-black tracking-[-0.06em] text-slate-950 sm:text-6xl">
      {teamMembers[memberIndex].slice(0, visibleLength)}
      <span aria-hidden="true" className="ml-1 inline-block h-[0.9em] w-[3px] animate-pulse bg-slate-950" />
    </span>
  );
}

function Logo() {
  return <Link href="/" className="flex items-center gap-2.5" aria-label="Miracle Birds home"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500 text-lg shadow-lg shadow-sky-200">🐦</span><span className="text-[17px] font-semibold tracking-[-0.02em] text-slate-950">Miracle Birds</span></Link>;
}

function ProductPreview() {
  return <div className="relative mx-auto mt-16 max-w-5xl">
    <div className="absolute -inset-8 rounded-[2.5rem] bg-sky-200/40 blur-3xl" />
    <div className="relative overflow-hidden rounded-[1.6rem] border border-slate-200 bg-white text-left shadow-[0_30px_90px_-28px_rgba(14,116,144,0.35)]">
      <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/80 px-5 py-4 sm:px-7">
        <div className="flex items-center gap-3"><div className="h-2.5 w-2.5 rounded-full bg-sky-500" /><span className="text-sm font-semibold text-slate-900">Revenue intelligence</span></div>
        <div className="hidden items-center gap-5 text-xs font-medium text-slate-400 sm:flex"><span>Overview</span><span>Customers</span><span>Workflows</span><span className="rounded-lg bg-sky-50 px-3 py-1.5 text-sky-600">This month⌄</span></div>
      </div>
      <div className="grid gap-5 bg-[#f8fbff] p-5 sm:p-7 lg:grid-cols-[1.35fr_0.65fr]">
        <div className="space-y-5">
          <div><p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-400">Good morning, team</p><h3 className="mt-1 text-2xl font-semibold tracking-[-0.04em] text-slate-950">Your customer pulse is clear.</h3></div>
          <div className="grid grid-cols-3 gap-3">
            {[['$2.4M', 'Pipeline'], ['87%', 'Healthy accounts'], ['+18%', 'Win rate']].map(([value, label]) => <div key={label} className="rounded-xl border border-slate-100 bg-white p-3 shadow-sm"><p className="text-lg font-semibold text-slate-950">{value}</p><p className="mt-1 text-[11px] text-slate-400">{label}</p></div>)}
          </div>
          <div className="rounded-xl border border-slate-100 bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><div><p className="text-sm font-semibold text-slate-900">Pipeline velocity</p><p className="mt-1 text-xs text-slate-400">Last 6 months</p></div><BarChart3 className="text-sky-500" size={20} /></div><div className="mt-6 flex h-28 items-end gap-2 sm:gap-3">{[35, 52, 44, 70, 63, 92, 78, 100, 86, 106, 94, 116].map((height, i) => <div key={i} className={`flex-1 rounded-t-md ${i > 7 ? 'bg-sky-500' : 'bg-sky-100'}`} style={{ height }} />)}</div></div>
        </div>
        <div className="rounded-xl border border-slate-100 bg-white p-5 shadow-sm"><div className="flex items-center justify-between"><p className="text-sm font-semibold text-slate-900">AI signals</p><Sparkles size={17} className="text-sky-500" /></div><div className="mt-5 space-y-3">{[['Northstar Labs', 'High intent', 'bg-emerald-50 text-emerald-600'], ['Orion Systems', 'At risk', 'bg-amber-50 text-amber-600'], ['Vertex Health', 'Expansion', 'bg-sky-50 text-sky-600']].map(([name, signal, cls]) => <div key={name} className="flex items-center justify-between rounded-lg border border-slate-100 p-3"><div><p className="text-xs font-semibold text-slate-800">{name}</p><p className="mt-1 text-[11px] text-slate-400">Suggested next step</p></div><span className={`rounded-full px-2 py-1 text-[10px] font-semibold ${cls}`}>{signal}</span></div>)}</div><button className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 py-2.5 text-xs font-semibold text-white">Open workspace <ArrowRight size={14} /></button></div>
      </div>
    </div>
  </div>;
}

export default function LandingPage() {
  const [mobileOpen, setMobileOpen] = useState(false);
  return <div className="min-h-screen overflow-hidden bg-[#fbfdff] text-slate-950 selection:bg-sky-200">
    <header className="sticky top-0 z-50 border-b border-slate-200/70 bg-[#fbfdff]/85 backdrop-blur-xl"><div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-8"><Logo /><nav className="hidden items-center gap-8 text-sm font-medium text-slate-500 md:flex"><a href="#product" className="transition hover:text-sky-600">Product</a><a href="#why" className="transition hover:text-sky-600">Why Miracle Birds</a><a href="#team" className="transition hover:text-sky-600">Team</a></nav><div className="hidden items-center gap-5 md:flex"><Link href="/login" className="text-sm font-semibold text-slate-500 transition hover:text-slate-950">Sign in</Link><Link href="/register" className="rounded-full bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-slate-300 transition hover:-translate-y-0.5 hover:bg-sky-600">Get started <ArrowRight size={15} className="ml-1 inline" /></Link></div><button aria-label={mobileOpen ? 'Close menu' : 'Open menu'} className="rounded-lg p-2 text-slate-700 md:hidden" onClick={() => setMobileOpen(!mobileOpen)}>{mobileOpen ? <X size={22} /> : <Menu size={22} />}</button></div>{mobileOpen && <div className="border-t border-slate-100 bg-white px-5 py-5 md:hidden"><nav className="flex flex-col gap-5 text-sm font-medium text-slate-600"><a href="#product" onClick={() => setMobileOpen(false)}>Product</a><a href="#why" onClick={() => setMobileOpen(false)}>Why Miracle Birds</a><a href="#team" onClick={() => setMobileOpen(false)}>Team</a><Link href="/login">Sign in</Link><Link href="/register" className="w-fit rounded-full bg-slate-950 px-5 py-2.5 text-white">Get started <ArrowRight size={15} className="ml-1 inline" /></Link></nav></div>}</header>
    <main>
      <section className="relative px-5 pb-20 pt-20 sm:px-8 sm:pt-28"><div className="pointer-events-none absolute left-1/2 top-0 -z-10 h-[600px] w-[900px] -translate-x-1/2 rounded-full bg-sky-100/70 blur-3xl" /><div className="mx-auto max-w-4xl text-center"><div className="mx-auto mb-7 inline-flex items-center gap-2 rounded-full border border-sky-200 bg-white/80 px-3.5 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-sky-700 shadow-sm"><ShieldCheck size={15} /> Intelligence you can trust</div><h1 className="text-[clamp(3.2rem,8vw,6.8rem)] font-semibold leading-[0.93] tracking-[-0.075em] text-slate-950">Make every customer<br /><span className="text-sky-500">count.</span></h1><p className="mx-auto mt-7 max-w-2xl text-lg leading-8 text-slate-500 sm:text-xl">Miracle Birds turns your CRM into a clear, intelligent growth system — so your team can see what is next and act with confidence.</p><div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row"><Link href="/register" className="rounded-full bg-sky-500 px-7 py-3.5 text-sm font-semibold text-white shadow-xl shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-600">Start building momentum <ArrowRight size={16} className="ml-1 inline" /></Link><a href="#product" className="rounded-full border border-slate-200 bg-white px-7 py-3.5 text-sm font-semibold text-slate-700 transition hover:border-sky-300 hover:text-sky-600">See how it works <ChevronDown size={16} className="ml-1 inline" /></a></div><div className="mt-7 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs font-medium text-slate-400"><span className="inline-flex items-center gap-1.5"><Check size={14} className="text-emerald-500" /> Secure by OWASP Top 10</span><span className="inline-flex items-center gap-1.5"><Check size={14} className="text-emerald-500" /> Built for your team</span><span className="inline-flex items-center gap-1.5"><Check size={14} className="text-emerald-500" /> Ready in minutes</span></div></div><div id="product"><ProductPreview /></div></section>
      <section id="why" className="border-y border-slate-200/80 bg-white px-5 py-24 sm:px-8"><div className="mx-auto max-w-7xl"><div className="max-w-xl"><p className="text-xs font-bold uppercase tracking-[0.18em] text-sky-600">A smarter operating layer</p><h2 className="mt-4 text-4xl font-semibold tracking-[-0.06em] text-slate-950 sm:text-5xl">Less searching.<br />More meaningful work.</h2></div><div className="mt-14 grid gap-4 md:grid-cols-3">{features.map(({ icon: Icon, title, copy }, index) => <article key={title} className="rounded-2xl border border-slate-200 bg-[#fbfdff] p-7 transition hover:-translate-y-1 hover:border-sky-200 hover:shadow-xl hover:shadow-sky-100/60"><div className={`flex h-11 w-11 items-center justify-center rounded-xl ${index === 1 ? 'bg-sky-500 text-white' : 'bg-sky-50 text-sky-600'}`}><Icon size={21} /></div><h3 className="mt-7 text-xl font-semibold tracking-[-0.03em]">{title}</h3><p className="mt-3 text-sm leading-7 text-slate-500">{copy}</p></article>)}</div></div></section>
      <section id="team" className="bg-[#f1f9ff] px-5 py-24 sm:px-8"><div className="mx-auto max-w-5xl text-center"><div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-sky-500 shadow-sm"><Layers3 size={22} /></div><p className="mt-6 text-xs font-bold uppercase tracking-[0.18em] text-sky-600">Built with purpose</p><h2 className="mt-4 text-4xl font-semibold tracking-[-0.06em] text-slate-950 sm:text-5xl">Built by</h2><div className="mt-5"><TeamTypewriter /></div><p className="mx-auto mt-6 max-w-xl text-base leading-7 text-slate-500">A focused team building a more human, useful intelligence layer for the people who care about customer relationships.</p></div></section>
      <section className="px-5 py-24 sm:px-8"><div className="mx-auto max-w-5xl overflow-hidden rounded-[2rem] bg-slate-950 px-7 py-16 text-center text-white shadow-2xl shadow-slate-300 sm:px-12"><div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-sky-500"><CircleDollarSign size={21} /></div><h2 className="mt-6 text-4xl font-semibold tracking-[-0.06em] sm:text-5xl">Your next best move<br /><span className="text-sky-400">starts here.</span></h2><p className="mx-auto mt-5 max-w-lg text-sm leading-7 text-slate-400">Bring your customer intelligence into focus and give your team more time for the work that moves the business forward.</p><Link href="/register" className="mt-8 inline-flex items-center rounded-full bg-white px-6 py-3.5 text-sm font-semibold text-slate-950 transition hover:bg-sky-100">Get started free <ArrowRight size={16} className="ml-2" /></Link></div></section>
    </main>
    <footer className="border-t border-slate-200 px-5 py-8 sm:px-8"><div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 text-center sm:flex-row sm:text-left"><Logo /><p className="text-xs text-slate-400">© 2026 Miracle Birds · Built by Ashlin Mirsha RK, Lohit A & Benesha Mercy Ramesh RA</p></div></footer>
  </div>;
}
