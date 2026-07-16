import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  CalendarDays,
  ChevronDown,
  ChevronUp,
  Loader2,
  StickyNote,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { AnalysisReport } from "../../performances/pages/PerformanceDetail";
import type { AnalysisResult } from "../../performances/types/analysis";
import {
  addNote,
  deleteNote,
  getAthleteProfile,
  getConnectedAthletePerformances,
  getConnectedPerformanceById,
  getNotesForConnection,
} from "../services/connections.service";
import { usePartnerConnections } from "../hooks/usePartnerConnections";
import { getConnectionViewState } from "../lib/getConnectionViewState";
import { useQueryClient, useMutation } from "@tanstack/react-query";

function formatDate(date?: string | null) {
  if (!date) return "Date unavailable";
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

function getStatusClasses(status: string | null) {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-700";
    case "processing":
    case "analyzing":
      return "bg-blue-100 text-blue-700";
    case "failed":
      return "bg-red-100 text-red-700";
    default:
      return "bg-orange-100 text-[#F0600E]";
  }
}

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    return (events[0] as { name?: string } | undefined)?.name ?? "Performance";
  }
  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }
  return "Performance";
}

function PerformanceCard({ performance }: { performance: any }) {
  const [expanded, setExpanded] = useState(false);

  const { data: full, isLoading } = useQuery({
    queryKey: ["coach-performance-detail", performance.id],
    queryFn: async () => {
      const { data, error } = await getConnectedPerformanceById(performance.id);
      if (error) throw new Error(error.message);
      return data;
    },
    enabled: expanded,
  });

  return (
    <div className="rounded-3xl border border-gray-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between p-5 text-left"
      >
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
              #{String(performance.performance_number ?? 0).padStart(2, "0")}
            </p>
            <span
              className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(performance.upload_status)}`}
            >
              {performance.upload_status ?? "uploaded"}
            </span>
          </div>
          <h3 className="mt-2 text-lg font-bold text-gray-950">{performance.title}</h3>
          <p className="mt-1 flex items-center gap-2 text-sm text-gray-500">
            <CalendarDays className="h-4 w-4" />
            {formatDate(performance.performance_date)}
            <span aria-hidden="true">·</span>
            {getEventName(performance.events)}
          </p>
        </div>

        {expanded ? (
          <ChevronUp className="h-5 w-5 shrink-0 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 shrink-0 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-gray-100 p-5">
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Loader2 className="h-4 w-4 animate-spin text-[#F0600E]" />
              Loading report...
            </div>
          )}

          {!isLoading && full?.upload_status === "completed" && full.analysis_result ? (
            <AnalysisReport result={full.analysis_result as AnalysisResult} />
          ) : (
            !isLoading && (
              <p className="text-sm text-gray-500">
                {full?.upload_status === "failed"
                  ? (full.analysis_error as string | null) ?? "Analysis failed for this recording."
                  : "No report available for this performance yet."}
              </p>
            )
          )}
        </div>
      )}
    </div>
  );
}

export default function PartnerAthleteDetail() {
  const { athleteId } = useParams();
  const { user, role } = useAuth();
  const isAcademy = role === "academy";
  const routeSet = isAcademy ? ROUTES.ACADEMY : ROUTES.COACH;
  const queryClient = useQueryClient();
  const [noteDraft, setNoteDraft] = useState("");

  const { data: connections = [], isLoading: connectionsLoading } = usePartnerConnections(user?.id);
  const connection = connections.find((c) => c.athlete_id === athleteId);
  const isConnected =
    connection && user && getConnectionViewState(connection, user.id) === "connected";

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["partner-athlete-profile", athleteId],
    queryFn: async () => {
      const { data, error } = await getAthleteProfile(athleteId!);
      if (error) throw new Error(error.message);
      return data;
    },
    enabled: Boolean(isConnected && athleteId),
  });

  const { data: performances = [], isLoading: performancesLoading } = useQuery({
    queryKey: ["coach-athlete-performances", athleteId],
    queryFn: async () => {
      const { data, error } = await getConnectedAthletePerformances(athleteId!);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(isConnected && athleteId),
  });

  const { data: notes = [], isLoading: notesLoading } = useQuery({
    queryKey: ["coach-notes", connection?.id],
    queryFn: async () => {
      const { data, error } = await getNotesForConnection(connection!.id);
      if (error) throw new Error(error.message);
      return data ?? [];
    },
    enabled: Boolean(isConnected && connection),
  });

  const addNoteMutation = useMutation({
    mutationFn: async () => {
      if (!connection || !user || !noteDraft.trim()) return null;
      const { data, error } = await addNote(connection.id, user.id, noteDraft.trim());
      if (error) throw new Error(error.message);
      return data;
    },
    onSuccess: () => {
      setNoteDraft("");
      queryClient.invalidateQueries({ queryKey: ["coach-notes", connection?.id] });
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: async (noteId: string) => {
      const { error } = await deleteNote(noteId);
      if (error) throw new Error(error.message);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["coach-notes", connection?.id] });
    },
  });

  if (connectionsLoading) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-[#F0600E]" />
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center">
        <h1 className="text-2xl font-bold text-red-700">
          You don't have access to this athlete.
        </h1>
        <p className="mt-2 text-sm text-red-600">
          A connection must be accepted before their profile becomes visible.
        </p>
        <Link
          to={routeSet.ATHLETES}
          className="mt-6 inline-flex rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white"
        >
          Back to {isAcademy ? "Squad" : "My Athletes"}
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl">
      <Link
        to={routeSet.ATHLETES}
        className="inline-flex items-center gap-2 text-sm font-bold text-gray-600 transition hover:text-[#F0600E]"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to {isAcademy ? "Squad" : "My Athletes"}
      </Link>

      <div className="mt-6 rounded-4xl border border-gray-200 bg-white p-7 shadow-xl shadow-gray-200/60 md:p-9">
        <h1 className="font-['Anton'] text-4xl uppercase leading-none text-gray-950 md:text-5xl">
          {connection?.athleteProfile?.full_name ?? "Athlete"}
        </h1>
        <p className="mt-2 text-sm text-gray-500">{connection?.athleteProfile?.email}</p>

        {profileLoading && (
          <div className="mt-6 flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin text-[#F0600E]" />
            Loading profile...
          </div>
        )}

        {!profileLoading && profile && (
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-gray-400">
                Preferred Event
              </p>
              <p className="mt-2 text-lg font-bold text-gray-950">
                {profile.preferred_event ?? "N/A"}
              </p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-gray-400">
                Personal Best
              </p>
              <p className="mt-2 text-lg font-bold text-gray-950">
                {profile.personal_best ?? "N/A"}
              </p>
            </div>
            <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-gray-400">
                Academy
              </p>
              <p className="mt-2 text-lg font-bold text-gray-950">
                {profile.academy ?? "N/A"}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8">
        <p className="mb-4 font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-gray-400">
          Performance History
        </p>

        {performancesLoading && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin text-[#F0600E]" />
            Loading performances...
          </div>
        )}

        {!performancesLoading && performances.length === 0 && (
          <p className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-6 text-sm text-gray-500">
            This athlete hasn't uploaded any performances yet.
          </p>
        )}

        {!performancesLoading && performances.length > 0 && (
          <div className="space-y-3">
            {performances.map((performance: any) => (
              <PerformanceCard key={performance.id} performance={performance} />
            ))}
          </div>
        )}
      </div>

      <div className="mt-8 rounded-4xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <StickyNote className="h-5 w-5 text-[#F0600E]" />
          <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-gray-400">
            Private Notes
          </p>
        </div>
        <p className="mt-2 text-sm text-gray-500">
          Only visible to you - never shared with this athlete.
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <textarea
            value={noteDraft}
            onChange={(e) => setNoteDraft(e.target.value)}
            placeholder="Add a private note about this athlete..."
            rows={2}
            className="w-full flex-1 rounded-xl border border-gray-300 p-3 text-sm focus:border-[#F0600E] focus:outline-none"
          />
          <button
            type="button"
            disabled={addNoteMutation.isPending || !noteDraft.trim()}
            onClick={() => addNoteMutation.mutate()}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {addNoteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Add Note
          </button>
        </div>

        {notesLoading && (
          <p className="mt-4 text-sm text-gray-500">Loading notes...</p>
        )}

        {!notesLoading && notes.length > 0 && (
          <div className="mt-5 space-y-3">
            {notes.map((note) => (
              <div
                key={note.id}
                className="flex items-start justify-between gap-3 rounded-2xl border border-gray-200 bg-gray-50 p-4"
              >
                <div>
                  <p className="text-sm leading-6 text-gray-700">{note.note}</p>
                  <p className="mt-1 text-xs text-gray-400">{formatDate(note.created_at)}</p>
                </div>
                <button
                  type="button"
                  onClick={() => deleteNoteMutation.mutate(note.id)}
                  className="shrink-0 text-gray-400 transition hover:text-red-600"
                  aria-label="Delete note"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
