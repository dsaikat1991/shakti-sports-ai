import {
  ArrowRight,
  CalendarDays,
  FileText,
  FileVideo,
  Loader2,
  Search,
} from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import EmptyState from "../../../components/shared/EmptyState";
import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePerformances } from "../../performances/hooks/usePerformances";
import { RatingBadge } from "../../performances/pages/PerformanceDetail";

const EVENT_OPTIONS = ["Sprint", "Hurdles", "Long Jump", "High Jump"];

type SortOption = "newest" | "oldest" | "readiness";

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    return (events[0] as { name?: string } | undefined)?.name ?? "Performance";
  }
  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }
  return "Performance";
}

function formatDate(date?: string | null) {
  if (!date) return "Date unavailable";
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

// A "report" here means a completed analysis with a real result - not
// just an uploaded/processing performance (that's what Performance
// History is for). Pulls the same fields the full detail report shows,
// just compacted into one row.
function extractReportSummary(analysisResult: unknown) {
  if (!analysisResult || typeof analysisResult !== "object") return null;
  const result = analysisResult as any;

  return {
    rating: result?.recording_quality?.rating as string | undefined,
    readinessScore: result?.recording_quality?.analysis_readiness?.score as
      | number
      | undefined,
    detectionRate: result?.analysis?.detection_rate_percent as
      | number
      | undefined,
    cameraView: result?.recording_quality?.camera_view?.classification as
      | string
      | undefined,
    biomechanicsReady: result?.biomechanics?.status !== "skipped",
  };
}

export default function AthleteReports() {
  const { user } = useAuth();
  const { data: performances = [], isLoading, error } = usePerformances(user?.id);

  const [search, setSearch] = useState("");
  const [eventFilter, setEventFilter] = useState("all");
  const [sortBy, setSortBy] = useState<SortOption>("newest");

  const reports = useMemo(() => {
    return performances
      .filter((p) => p.upload_status === "completed" && Boolean(p.analysis_result))
      .map((p) => ({ performance: p, summary: extractReportSummary(p.analysis_result) }));
  }, [performances]);

  const visibleReports = useMemo(() => {
    const query = search.trim().toLowerCase();

    const filtered = reports.filter(({ performance }) => {
      if (eventFilter !== "all" && getEventName(performance.events) !== eventFilter) {
        return false;
      }
      if (query) {
        const haystack = `${performance.title ?? ""} ${performance.notes ?? ""}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      return true;
    });

    const sorted = [...filtered];
    if (sortBy === "newest") {
      sorted.sort(
        (a, b) =>
          new Date(b.performance.created_at ?? 0).getTime() -
          new Date(a.performance.created_at ?? 0).getTime(),
      );
    } else if (sortBy === "oldest") {
      sorted.sort(
        (a, b) =>
          new Date(a.performance.created_at ?? 0).getTime() -
          new Date(b.performance.created_at ?? 0).getTime(),
      );
    } else {
      sorted.sort(
        (a, b) => (b.summary?.readinessScore ?? 0) - (a.summary?.readinessScore ?? 0),
      );
    }

    return sorted;
  }, [reports, search, eventFilter, sortBy]);

  return (
    <div className="mx-auto max-w-6xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        AI Reports
      </p>

      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Your Reports
      </h1>

      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Every completed Shakti Motion Intelligence™ analysis, in one place.
        Still-processing or failed uploads live on the Performances page.
      </p>

      {!isLoading && !error && reports.length > 0 && (
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
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm outline-none focus:border-[#F0600E]"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="readiness">Highest readiness score</option>
          </select>
        </div>
      )}

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your reports...
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
          title="No reports yet"
          description="Upload your first performance to generate your first Shakti Motion Intelligence™ report."
          action={
            <Link
              to={ROUTES.ATHLETE.NEW_PERFORMANCE}
              className="mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
            >
              Start First Performance
            </Link>
          }
        />
      )}

      {!isLoading && !error && performances.length > 0 && reports.length === 0 && (
        <EmptyState
          icon={FileText}
          tone="neutral"
          title="No completed reports yet"
          description={
            <>
              Your uploads are still processing or didn't complete. Check{" "}
              <Link to={ROUTES.ATHLETE.HISTORY} className="font-bold text-[#F0600E] hover:text-orange-700">
                Performances
              </Link>{" "}
              for their current status.
            </>
          }
        />
      )}

      {!isLoading && reports.length > 0 && visibleReports.length === 0 && (
        <EmptyState
          icon={Search}
          tone="neutral"
          title="No matches"
          description="Try a different search term or event filter."
        />
      )}

      {!isLoading && visibleReports.length > 0 && (
        <div className="mt-6 space-y-4">
          {visibleReports.map(({ performance, summary }) => (
            <Link
              key={performance.id}
              to={ROUTES.ATHLETE.PERFORMANCE_REPORT(performance.id)}
              className="group block rounded-4xl border border-gray-200 bg-white p-6 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-orange-200 hover:shadow-xl hover:shadow-gray-200/70"
            >
              <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-center">
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
                      Performance #
                      {String(performance.performance_number ?? 0).padStart(2, "0")}
                    </p>

                    <RatingBadge rating={summary?.rating} />

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-bold ${
                        summary?.biomechanicsReady
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {summary?.biomechanicsReady ? "Biomechanics included" : "Biomechanics skipped"}
                    </span>
                  </div>

                  <h2 className="mt-3 text-2xl font-bold text-gray-950">
                    {performance.title}
                  </h2>

                  <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-500">
                    <CalendarDays className="h-4 w-4" />
                    <span>{formatDate(performance.performance_date)}</span>
                    <span aria-hidden="true">·</span>
                    <span>{getEventName(performance.events)}</span>
                    {summary?.cameraView && (
                      <>
                        <span aria-hidden="true">·</span>
                        <span>{summary.cameraView}</span>
                      </>
                    )}
                  </p>
                </div>

                <div className="flex shrink-0 items-center gap-6">
                  {typeof summary?.readinessScore === "number" && (
                    <div className="text-center">
                      <p className="text-2xl font-black text-gray-950">
                        {Math.round(summary.readinessScore)}
                      </p>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                        Readiness
                      </p>
                    </div>
                  )}

                  {typeof summary?.detectionRate === "number" && (
                    <div className="text-center">
                      <p className="text-2xl font-black text-gray-950">
                        {Math.round(summary.detectionRate)}%
                      </p>
                      <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                        Detection
                      </p>
                    </div>
                  )}

                  <ArrowRight className="h-5 w-5 shrink-0 text-gray-400 transition group-hover:translate-x-1 group-hover:text-[#F0600E]" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
