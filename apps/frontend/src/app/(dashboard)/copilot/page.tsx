"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, Loader2, X, Plus, MessageSquare, Bell, TrendingDown, FileText, DollarSign } from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const MODELS = [
  { id: 'big-pickle', label: 'Big Pickle' },
  { id: 'mimo-v2.5-free', label: 'MiMo V2.5' },
  { id: 'hy3-free', label: 'Hy3' },
  { id: 'laguna-s-2.1-free', label: 'Laguna S 2.1' },
  { id: 'nemotron-3-ultra-free', label: 'Nemotron 3 Ultra' },
  { id: 'nemotron-3.5-lightning-free', label: 'Nemotron 3.5 Lightning' },
  { id: 'deepseek-v4-flash-free', label: 'DeepSeek V4 Flash' },
] as const;

const STARTER_PROMPTS = [
  { label: "Which customers need attention today?", icon: Bell },
  { label: "Show customers likely to churn.", icon: TrendingDown },
  { label: "Summarize TechGlobal account.", icon: FileText },
  { label: "Why did revenue decrease?", icon: DollarSign },
];

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-1 py-0.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-2 w-2 rounded-full bg-slate-400 dark:bg-slate-500 animate-bounce"
          style={{ animationDelay: `${i * 150}ms` }}
        />
      ))}
    </div>
  );
}

export default function CopilotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello! I'm the Miracle Birds AI Copilot. I'm connected to your CRM and can help you with:\n\n• **Summarize accounts** — Get instant account health summaries\n• **Churn predictions** — Identify at-risk customers\n• **Next best actions** — AI-driven sales recommendations\n• **Pipeline analysis** — Revenue forecasts and deal insights\n\nHow can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState('deepseek-v4-flash-free');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMsg: Message = { role: "user", content: content.trim(), timestamp: new Date() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await apiClient.post("/copilot/chat", { message: content.trim(), model: selectedModel });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.response, timestamp: new Date() },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I'm having trouble connecting to the intelligence engine right now. Please try again in a moment.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  function renderContent(content: string) {
    // Simple bold markdown support
    const parts = content.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return <span key={i}>{part}</span>;
    });
  }

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-dark-border dark:bg-dark-bg">
      {/* Header */}
      <div className="flex shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6 py-4 dark:border-dark-border dark:bg-dark-bg/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500 text-white dark:bg-sky-500 dark:text-white">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 dark:text-white">AI CRM Copilot</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Miracle Birds Intelligence — connected to your CRM
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 mr-2">
            <label className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Model:</label>
            <select
              value={selectedModel}
              onChange={(e) => {
                setSelectedModel(e.target.value);
                setMessages([
                  {
                    role: "assistant",
                    content: `Switched to model: ${MODELS.find(m => m.id === e.target.value)?.label}. How can I help you?`,
                    timestamp: new Date(),
                  },
                ]);
              }}
              className="rounded-lg border border-slate-200 dark:border-dark-border bg-white dark:bg-dark-surface text-xs px-2 py-1 text-slate-700 dark:text-white focus:outline-none"
            >
              {MODELS.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
          <span className="flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:border-emerald-800/40 dark:bg-emerald-950/20 dark:text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live
          </span>
          <button
            onClick={() =>
              setMessages([
                {
                  role: "assistant",
                  content: "Conversation cleared. How can I help you?",
                  timestamp: new Date(),
                },
              ])
            }
            className="rounded-lg border border-slate-200 p-1.5 text-slate-400 hover:bg-slate-50 hover:text-slate-700 dark:border-dark-border dark:hover:bg-dark-surface dark:hover:text-white"
            title="Clear conversation"
          >
            <Plus className="h-4 w-4 rotate-45" />
          </button>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold
                ${m.role === "assistant"
                  ? "bg-sky-500 text-white dark:bg-sky-500 dark:text-white"
                  : "bg-slate-100 text-slate-600 dark:bg-dark-surface dark:text-slate-300"
                }`}
            >
              {m.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
            </div>

            {/* Bubble */}
            <div
              className={`group relative max-w-[78%] space-y-1
                ${m.role === "user" ? "items-end" : "items-start"} flex flex-col`}
            >
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed
                  ${m.role === "user"
                    ? "rounded-tr-sm bg-slate-900 text-white dark:bg-white dark:text-slate-900"
                    : "rounded-tl-sm border border-slate-200 bg-white text-slate-800 dark:border-dark-border dark:bg-dark-surface dark:text-slate-200"
                  }`}
              >
                <p className="whitespace-pre-wrap">{renderContent(m.content)}</p>
              </div>
              <span className="px-1 text-[10px] text-slate-400 dark:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                {formatTime(m.timestamp)}
              </span>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-500 text-white dark:bg-sky-500 dark:text-white">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="rounded-2xl rounded-tl-sm border border-slate-200 bg-white px-4 py-3 dark:border-dark-border dark:bg-dark-surface">
              <TypingDots />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Bottom area */}
      <div className="shrink-0 border-t border-slate-200 bg-white px-6 pb-6 pt-4 dark:border-dark-border dark:bg-dark-bg/80">
        {/* Starter prompts — only show when there's just the welcome message */}
        {messages.length === 1 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {STARTER_PROMPTS.map((p, i) => (
              <button
                key={i}
                onClick={() => sendMessage(p.label)}
                className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-slate-300 hover:bg-white hover:shadow-sm dark:border-dark-border dark:bg-dark-surface dark:text-slate-300 dark:hover:bg-dark-bg"
              >
                <p.icon className="h-3.5 w-3.5 text-sky-500" />
                {p.label}
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleFormSubmit} className="relative flex items-end gap-2">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-resize
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your customers, pipelines, or CRM data…"
            className="flex-1 resize-none overflow-hidden rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-sm text-slate-900 placeholder-slate-400 focus:border-slate-400 focus:bg-white focus:outline-none focus:ring-0 dark:border-dark-border dark:bg-dark-surface dark:text-white dark:placeholder-slate-500 dark:focus:border-slate-600 dark:focus:bg-dark-bg/80"
            style={{ minHeight: "48px" }}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute bottom-2 right-2 flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500 text-white transition hover:bg-sky-600 disabled:opacity-40 dark:bg-sky-500 dark:text-white dark:hover:bg-sky-400"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </form>
        <p className="mt-2 text-center text-[10px] text-slate-400 dark:text-slate-600">
          AI Copilot can make mistakes. Always verify critical decisions.
        </p>
      </div>
    </div>
  );
}
