import {
  ArrowRight,
  CalendarDays,
  FileVideo,
  Loader2,
  Plus,
  Search,
  ShieldCheck,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import EmptyState from "../../../components/shared/EmptyState";
import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePerformances } from "../hooks/usePerformances";
import { formatSessionDate } from "../lib/analysisSummary";
import { buildPerformanceDisplayName } from "../lib/performanceDisplayName";

const EVENT_OPTIONS = ["Sprint", "Hurdles", "Long Jump", "High Jump"];
const STATUS_OPTIONS = ["uploaded", "analyzing", "processing", "completed", "failed"];

type SortOption = "newest" | "oldest" | "status";

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as { name?: string } | undefined;
    return firstEvent?.name ?? "Performance";
  }

  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }

  return "Performance";
}

function getStatusLabel(status: string | null) {
  switch (status) {
    case "completed":
      return "Completed";

    case "processing":
      return "Processing";

    case "analyzing":
      return "Analyzing";

    case "failed":
      return "Failed";

    default:
      return "Uploaded";
  }
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

function getRecordingQualityRating(analysisResult: unknown): string | null {
  if (!analysisResult || typeof analysisResult !== "object") return null;
  const quality = (analysisResult as any).recording_quality;
  return quality?.rating ?? null;
}

function isReportAvailable(performance: { upload_status: string | null; analysis_result: unknown }) {
  return performance.upload_status === "completed" && Boolean(performance.analysis_result);
}


export default function PerformanceHistory() {
  const { user } = useAuth();

  const {
    data: performances = [],
    isLoading,
    error,
  } = usePerformances(user?.id);

  const [search, setSearch] = useState("");
  const [eventFilter, setEventFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState<SortOption>("newest");

  const visiblePerformances = useMemo(() => {
    const query = search.trim().toLowerCase();

    const filtered = performances.filter((performance) => {
      if (eventFilter !== "all" && getEventName(performance.events) !== eventFilter) {
        return false;
      }
      if (statusFilter !== "all" && (performance.upload_status ?? "uploaded") !== statusFilter) {
        return false;
      }
      if (query) {
        const haystack = `${buildPerformanceDisplayName(performance)} ${performance.notes ?? ""}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });

    const sorted = [...filtered];
    if (sortBy === "newest") {
      sorted.sort(
        (a, b) => new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime(),
      );
    } else if (sortBy === "oldest") {
      sorted.sort(
        (a, b) => new Date(a.created_at ?? 0).getTime() - new Date(b.created_at ?? 0).getTime(),
      );
    } else {
      sorted.sort((a, b) =>
        (a.upload_status ?? "").localeCompare(b.upload_status ?? ""),
      );
    }

    return sorted;
  }, [performances, search, eventFilter, statusFilter, sortBy]);

  return (
    <div className="mx-auto max-w-6xl">
      <div className="flex flex-col justify-between gap-6 xl:flex-row xl:items-end">
        <div>
          <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
            My Performances
          </p>

          <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
            Performance History
          </h1>

          <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
            Review every uploaded session, follow its analysis status, and track
            your journey over time.
          </p>
        </div>

        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
        >
          <Plus className="h-4 w-4" />
          New Performance
        </Link>
      </div>

      {!isLoading && !error && performances.length > 0 && (
        <div className="mt-8 flex flex-col gap-3 rounded-3xl border border-gray-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by title or notes..."
              className="w-full rounded-xl border border-gray-200 py-2.5 pl-11 pr-4 text-sm outline-none focus:border-[#F0600E] focus:ring-4 focus:ring-orange-100"
            />
          </div>

          <select
            value={eventFilter}
            onChange={(e) => setEventFilter(e.target.value)}
            className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm outline-none focus:border-[#F0600E]"
          >
            <option value="all">All events</option>
            {EVENT_OPTIONS.map((event) => (
              <option key={event} value={event}>
                {event}
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm outline-none focus:border-[#F0600E]"
          >
            <option value="all">All statuses</option>
            {STATUS_OPTIONS.map((status) => (
              <option key={status} value={status}>
                {getStatusLabel(status)}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm outline-none focus:border-[#F0600E]"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="status">By status</option>
          </select>
        </div>
      )}

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your performances...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && !error && performances.length === 0 && (
        <EmptyState
          icon={FileVideo}
          title="No performances yet"
          description="Start your first session to create your timeline and prepare your first Shakti Motion Intelligence™ report."
          action={
            <Link
              to={ROUTES.ATHLETE.NEW_PERFORMANCE}
              className="mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
            >
              <Plus className="h-4 w-4" />
              Start First Performance
            </Link>
          }
        />
      )}

      {!isLoading && !error && performances.length > 0 && visiblePerformances.length === 0 && (
        <EmptyState
          icon={Search}
          tone="neutral"
          title="No matches"
          description="Try a different search term or clear your filters."
        />
      )}

      {!isLoading && visiblePerformances.length > 0 && (
        <div className="mt-6 space-y-4">
          {visiblePerformances.map((performance) => {
            const qualityRating = getRecordingQualityRating(performance.analysis_result);
            const reportAvailable = isReportAvailable(performance);

            return (
              <article
                key={performance.id}
                className="group rounded-4xl border border-gray-200 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-orange-200 hover:shadow-xl hover:shadow-gray-200/70"
              >
                <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
                  <div>
                    <div className="flex flex-wrap items-center gap-3">
                      <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
                        Performance #
                        {String(
                          performance.performance_number ?? 0,
                        ).padStart(2, "0")}
                      </p>

                      <span
                        className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(
                          performance.upload_status,
                        )}`}
                      >
                        {getStatusLabel(performance.upload_status)}
                      </span>

                      {qualityRating && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs font-bold text-gray-600">
                          <ShieldCheck className="h-3 w-3" />
                          {qualityRating}
                        </span>
                      )}

                      {reportAvailable && (
                        <span className="rounded-full bg-purple-100 px-3 py-1 text-xs font-bold text-purple-700">
                          Report Ready
                        </span>
                      )}
                    </div>

                    <h2 className="mt-3 text-2xl font-bold text-gray-950">
                      {buildPerformanceDisplayName(performance)}
                    </h2>

                    <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-500">
                      <CalendarDays className="h-4 w-4" />

                      <span>{formatSessionDate(performance.performance_date)}</span>

                      <span aria-hidden="true">·</span>

                      <span>{getEventName(performance.events)}</span>
                    </p>

                    {performance.notes && (
                      <p className="mt-3 max-w-2xl text-sm leading-6 text-gray-600">
                        {performance.notes}
                      </p>
                    )}
                  </div>

                  <Link
                    to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
                    className="inline-flex shrink-0 items-center gap-2 text-sm font-bold text-gray-700 transition group-hover:text-[#F0600E]"
                  >
                    View Performance
                    <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
                  </Link>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
