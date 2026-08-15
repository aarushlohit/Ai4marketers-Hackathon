"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import {
  Video,
  Plus,
  CheckCircle,
  AlertCircle,
  FileText,
  Send,
  Calendar,
  Clock,
  Smile,
  Trash2,
} from "lucide-react";

interface Meeting {
  id: string;
  customer_id: string;
  transcript_summary: string;
  action_items: Array<{ task: string; owner: string; due_date?: string }>;
  sentiment: string;
  created_at: string;
}

export default function MeetingsPage() {
  const qc = useQueryClient();
  const [customerId, setCustomerId] = useState("");
  const [transcript, setTranscript] = useState("");
  const [title, setTitle] = useState("");
  const [participants, setParticipants] = useState("");
  const [duration, setDuration] = useState(30);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch customers to link to the meeting
  const { data: customersData } = useQuery({
    queryKey: ["customers"],
    queryFn: () => apiClient.get("/customers").then((r) => r.data),
  });
  const customers = Array.isArray(customersData)
    ? customersData
    : (customersData?.customers ?? []);

  // Query analyzed meetings for first customer if available, or generally
  const activeCustomer = customerId || (customers[0]?.id ?? "");

  const { data: meetingsData, isLoading } = useQuery({
    queryKey: ["meetings", activeCustomer],
    queryFn: () => {
      if (!activeCustomer) return Promise.resolve([]);
      return apiClient.get(`/meetings/${activeCustomer}`).then((r) => r.data);
    },
    enabled: !!activeCustomer,
  });
  const meetings: Meeting[] = Array.isArray(meetingsData) ? meetingsData : [];

  const analyzeMutation = useMutation({
    mutationFn: (payload: any) =>
      apiClient.post("/meetings/analyze", payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["meetings", activeCustomer] });
      setTranscript("");
      setTitle("");
      setParticipants("");
      setIsSubmitting(false);
    },
    onError: () => {
      setIsSubmitting(false);
    },
  });

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeCustomer || !transcript) return;
    setIsSubmitting(true);
    analyzeMutation.mutate({
      customer_id: activeCustomer,
      title: title || "Client Review Call",
      date: new Date().toLocaleDateString(),
      participants: participants || "Account Executive, Client",
      duration_minutes: duration,
      transcript,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Meeting Intelligence
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Analyze audio or text transcripts to extract key notes, sentiment, and
          CRM actions.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left side: Upload / Input transcript */}
        <div className="lg:col-span-1 rounded-xl border bg-white p-6 shadow-sm space-y-4 h-fit dark:border-dark-border dark:bg-dark-surface">
          <h2 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2 border-b dark:border-dark-border pb-3">
            <Video className="h-5 w-5 text-blue-600" />
            Process New Meeting
          </h2>

          <form onSubmit={handleAnalyze} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Link Customer
              </label>
              <select
                value={customerId}
                onChange={(e) => setCustomerId(e.target.value)}
                className="w-full rounded-lg border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg dark:text-white"
              >
                <option value="">Select a Customer</option>
                {customers.map((c: any) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name} ({c.company})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Meeting Title
              </label>
              <input
                type="text"
                placeholder="Product Demo & Pricing"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-lg border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg dark:text-white dark:placeholder-dark-muted"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Participants
              </label>
              <input
                type="text"
                placeholder="Sarah (AE), John (Client)"
                value={participants}
                onChange={(e) => setParticipants(e.target.value)}
                className="w-full rounded-lg border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg dark:text-white dark:placeholder-dark-muted"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Transcript Text
              </label>
              <textarea
                placeholder="Paste call transcript here..."
                rows={6}
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                className="w-full rounded-lg border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none dark:border-dark-border dark:bg-dark-bg dark:text-white dark:placeholder-dark-muted"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting || !activeCustomer || !transcript}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isSubmitting ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  Analyze with OpenCode AI
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right side: Processed meetings list */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Analyzed Calls & Action Items
          </h2>

          {isLoading ? (
            <div className="space-y-4">
              {[...Array(2)].map((_, i) => (
                <div
                  key={i}
                  className="h-40 animate-pulse rounded-xl bg-gray-100"
                />
              ))}
            </div>
          ) : meetings.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-dashed bg-white py-24 text-center dark:border-dark-border dark:bg-dark-surface">
              <FileText className="h-10 w-10 text-gray-300" />
              <div>
                <p className="font-medium text-gray-700 dark:text-gray-300">
                  No meeting intelligence generated
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-500">
                  Select a customer and analyze a transcript to see summaries
                  and action plans here.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {meetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className="rounded-xl border bg-white p-6 shadow-sm space-y-4 dark:border-dark-border dark:bg-dark-surface"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-3">
                      <div className="rounded-lg bg-blue-50 p-2 text-blue-600">
                        <Video className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          Call Summary
                        </h3>
                        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-dark-muted mt-1">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3.5 w-3.5" />
                            {new Date(meeting.created_at).toLocaleDateString()}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3.5 w-3.5" />
                            Analyzed
                          </span>
                          <span className="flex items-center gap-1 capitalize">
                            <Smile className="h-3.5 w-3.5 text-green-500" />
                            Sentiment: {meeting.sentiment}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-dark-bg p-3 rounded-lg border dark:border-dark-border">
                    {meeting.transcript_summary}
                  </p>

                  {/* Action items */}
                  {meeting.action_items && meeting.action_items.length > 0 && (
                    <div className="space-y-2 border-t pt-3">
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-dark-muted">
                        Extracted Action Items
                      </h4>
                      <div className="space-y-2">
                        {meeting.action_items.map((item, idx) => (
                          <div
                            key={idx}
                            className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200 bg-green-50/30 dark:bg-dark-accent/5 border border-green-100 dark:border-dark-border rounded-lg p-2"
                          >
                            <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                            <span className="flex-1 font-medium">
                              {item.task}
                            </span>
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                              Owner: {item.owner}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
