import {
  ArrowRight,
  CalendarDays,
  FileVideo,
  Loader2,
  Plus,
} from "lucide-react";
import { Link } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { useAuth } from "../../auth/context/AuthContext";
import { usePerformances } from "../hooks/usePerformances";

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

function formatDate(date?: string | null) {
  if (!date) return "Date unavailable";

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

export default function PerformanceHistory() {
  const { user } = useAuth();

  const {
    data: performances = [],
    isLoading,
    error,
  } = usePerformances(user?.id);

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
        <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
          <FileVideo className="mx-auto h-11 w-11 text-gray-400" />

          <h2 className="mt-5 text-2xl font-bold text-gray-950">
            No performances yet
          </h2>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
            Start your first session to create your timeline and prepare your
            first Shakti Motion Intelligence™ report.
          </p>

          <Link
            to={ROUTES.ATHLETE.NEW_PERFORMANCE}
            className="mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
          >
            <Plus className="h-4 w-4" />
            Start First Performance
          </Link>
        </div>
      )}

      {!isLoading && performances.length > 0 && (
        <div className="mt-10 space-y-4">
          {performances.map((performance) => (
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
                  </div>

                  <h2 className="mt-3 text-2xl font-bold text-gray-950">
                    {performance.title}
                  </h2>

                  <p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-gray-500">
                    <CalendarDays className="h-4 w-4" />

                    <span>{formatDate(performance.performance_date)}</span>

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
          ))}
        </div>
      )}
    </div>
  );
}