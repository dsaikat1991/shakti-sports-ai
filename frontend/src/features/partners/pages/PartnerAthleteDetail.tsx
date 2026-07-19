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
import { formatSessionDate } from "../../performances/lib/analysisSummary";
import { buildPerformanceDisplayName } from "../../performances/lib/performanceDisplayName";
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

function getStatusClasses(status: string | null) {
  switch (status) {
    case "completed":
      return "bg-success-progress-soft text-success-progress";
    case "processing":
    case "analyzing":
      return "bg-info-insight-soft text-info-insight";
    case "failed":
      return "bg-error-failure-soft text-error-failure";
    default:
      return "bg-brand-action-soft text-brand-action";
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
    <div className="rounded-3xl border border-border-default bg-surface-card shadow-sm">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center justify-between p-5 text-left"
      >
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-brand-action">
              #{String(performance.performance_number ?? 0).padStart(2, "0")}
            </p>
            <span
              className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(performance.upload_status)}`}
            >
              {performance.upload_status ?? "uploaded"}
            </span>
          </div>
          <h3 className="mt-2 text-lg font-bold text-text-primary">{buildPerformanceDisplayName(performance)}</h3>
          <p className="mt-1 flex items-center gap-2 text-sm text-text-muted">
            <CalendarDays className="h-4 w-4" />
            {formatSessionDate(performance.performance_date)}
            <span aria-hidden="true">·</span>
            {getEventName(performance.events)}
          </p>
        </div>

        {expanded ? (
          <ChevronUp className="h-5 w-5 shrink-0 text-text-disabled" />
        ) : (
          <ChevronDown className="h-5 w-5 shrink-0 text-text-disabled" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-border-divider p-5">
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-text-muted">
              <Loader2 className="h-4 w-4 animate-spin text-brand-action" />
              Loading report...
            </div>
          )}

          {!isLoading && full?.upload_status === "completed" && full.analysis_result ? (
            <AnalysisReport result={full.analysis_result as AnalysisResult} />
          ) : (
            !isLoading && (
              <p className="text-sm text-text-muted">
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
      <div className="mx-auto max-w-5xl rounded-4xl border border-border-default bg-surface-card p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-brand-action" />
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-error-failure bg-error-failure-soft p-10 text-center">
        <h1 className="text-2xl font-bold text-error-failure">
          You don't have access to this athlete.
        </h1>
        <p className="mt-2 text-sm text-error-failure">
          A connection must be accepted before their profile becomes visible.
        </p>
        <Link
          to={routeSet.ATHLETES}
          className="mt-6 inline-flex rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white"
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
        className="inline-flex items-center gap-2 text-sm font-bold text-text-secondary transition hover:text-brand-action"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to {isAcademy ? "Squad" : "My Athletes"}
      </Link>

      <div className="mt-6 rounded-4xl border border-border-default bg-surface-card p-7 shadow-xl shadow-border-default/60 md:p-9">
        <h1 className="text-2xl font-bold text-text-primary md:text-3xl">
          {connection?.athleteProfile?.full_name ?? "Athlete"}
        </h1>
        <p className="mt-2 text-sm text-text-muted">{connection?.athleteProfile?.email}</p>

        {profileLoading && (
          <div className="mt-6 flex items-center gap-2 text-sm text-text-muted">
            <Loader2 className="h-4 w-4 animate-spin text-brand-action" />
            Loading profile...
          </div>
        )}

        {!profileLoading && profile && (
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-3xl border border-border-default bg-surface-sunken p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-text-disabled">
                Preferred Event
              </p>
              <p className="mt-2 text-lg font-bold text-text-primary">
                {profile.preferred_event ?? "N/A"}
              </p>
            </div>
            <div className="rounded-3xl border border-border-default bg-surface-sunken p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-text-disabled">
                Personal Best
              </p>
              <p className="mt-2 text-lg font-bold text-text-primary">
                {profile.personal_best ?? "N/A"}
              </p>
            </div>
            <div className="rounded-3xl border border-border-default bg-surface-sunken p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-text-disabled">
                Academy
              </p>
              <p className="mt-2 text-lg font-bold text-text-primary">
                {profile.academy ?? "N/A"}
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-text-disabled">
            Performance History
          </p>
          <Link
            to={routeSet.ATHLETE_PROGRESS(athleteId!)}
            className="text-sm font-bold text-brand-action hover:text-brand-action-hover"
          >
            View Progress Over Time →
          </Link>
        </div>

        {performancesLoading && (
          <div className="flex items-center gap-2 text-sm text-text-muted">
            <Loader2 className="h-4 w-4 animate-spin text-brand-action" />
            Loading performances...
          </div>
        )}

        {!performancesLoading && performances.length === 0 && (
          <p className="rounded-3xl border border-dashed border-border-default bg-surface-sunken p-6 text-sm text-text-muted">
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

      <div className="mt-8 rounded-4xl border border-border-default bg-surface-card p-6 shadow-sm">
        <div className="flex items-center gap-2">
          <StickyNote className="h-5 w-5 text-brand-action" />
          <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-text-disabled">
            Private Notes
          </p>
        </div>
        <p className="mt-2 text-sm text-text-muted">
          Only visible to you - never shared with this athlete.
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <textarea
            value={noteDraft}
            onChange={(e) => setNoteDraft(e.target.value)}
            placeholder="Add a private note about this athlete..."
            rows={2}
            className="w-full flex-1 rounded-xl border border-border-default p-3 text-sm focus:border-brand-action focus:outline-none"
          />
          <button
            type="button"
            disabled={addNoteMutation.isPending || !noteDraft.trim()}
            onClick={() => addNoteMutation.mutate()}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-brand-action px-5 py-3 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            {addNoteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Add Note
          </button>
        </div>

        {notesLoading && (
          <p className="mt-4 text-sm text-text-muted">Loading notes...</p>
        )}

        {!notesLoading && notes.length > 0 && (
          <div className="mt-5 space-y-3">
            {notes.map((note) => (
              <div
                key={note.id}
                className="flex items-start justify-between gap-3 rounded-2xl border border-border-default bg-surface-sunken p-4"
              >
                <div>
                  <p className="text-sm leading-6 text-text-secondary">{note.note}</p>
                  <p className="mt-1 text-xs text-text-disabled">{formatSessionDate(note.created_at)}</p>
                </div>
                <button
                  type="button"
                  onClick={() => deleteNoteMutation.mutate(note.id)}
                  className="shrink-0 text-text-disabled transition hover:text-error-failure"
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
