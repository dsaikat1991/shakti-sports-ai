import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock3,
  FileVideo,
  Loader2,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { usePerformance } from "../hooks/usePerformance";

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as
      | { name?: string; category?: string }
      | undefined;

    return firstEvent?.name ?? "Performance";
  }

  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }

  return "Performance";
}

function getEventCategory(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as
      | { name?: string; category?: string }
      | undefined;

    return firstEvent?.category ?? "Athletics";
  }

  if (events && typeof events === "object" && "category" in events) {
    return (events as { category?: string }).category ?? "Athletics";
  }

  return "Athletics";
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
    month: "long",
    year: "numeric",
  }).format(new Date(date));
}

export default function PerformanceDetail() {
  const { performanceId } = useParams();
  const { data: performance, isLoading, error } =
    usePerformance(performanceId);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-[#F0600E]" />

        <p className="mt-4 text-sm font-bold text-gray-600">
          Loading performance...
        </p>
      </div>
    );
  }

  if (error || !performance) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center">
        <h1 className="text-2xl font-bold text-red-700">
          Unable to load this performance.
        </h1>

        <Link
          to={ROUTES.ATHLETE.HISTORY}
          className="mt-6 inline-flex rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white"
        >
          Return to Performances
        </Link>
      </div>
    );
  }

  const status = performance.upload_status;
  const isProcessing =
    status === "uploaded" ||
    status === "processing" ||
    status === "analyzing";

  return (
    <div className="mx-auto max-w-6xl">
      <Link
        to={ROUTES.ATHLETE.HISTORY}
        className="inline-flex items-center gap-2 text-sm font-bold text-gray-600 transition hover:text-[#F0600E]"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to My Performances
      </Link>

      <div className="mt-6 rounded-4xl border border-gray-200 bg-white p-7 shadow-xl shadow-gray-200/60 md:p-9">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-start">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
                Performance #
                {String(performance.performance_number ?? 0).padStart(2, "0")}
              </p>

              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(
                  status,
                )}`}
              >
                {getStatusLabel(status)}
              </span>
            </div>

            <h1 className="mt-4 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
              {performance.title}
            </h1>

            <p className="mt-4 flex flex-wrap items-center gap-2 text-sm text-gray-500">
              <CalendarDays className="h-4 w-4" />
              {formatDate(performance.performance_date)}
              <span aria-hidden="true">·</span>
              {getEventName(performance.events)}
            </p>
          </div>

          {isProcessing && (
            <Link
              to={ROUTES.ATHLETE.PERFORMANCE_PROCESSING(performance.id)}
              className="inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
            >
              <Loader2 className="h-4 w-4 animate-spin" />
              View Analysis Status
            </Link>
          )}
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <FileVideo className="h-5 w-5 text-[#F0600E]" />

            <p className="mt-4 text-xs font-bold uppercase tracking-widest text-gray-400">
              Event
            </p>

            <p className="mt-2 text-xl font-bold text-gray-950">
              {getEventName(performance.events)}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              {getEventCategory(performance.events)}
            </p>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <Clock3 className="h-5 w-5 text-[#F0600E]" />

            <p className="mt-4 text-xs font-bold uppercase tracking-widest text-gray-400">
              Current Status
            </p>

            <p className="mt-2 text-xl font-bold text-gray-950">
              {getStatusLabel(status)}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              {isProcessing
                ? "Your performance report is being prepared."
                : "Your performance has been processed."}
            </p>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <CheckCircle2 className="h-5 w-5 text-green-700" />

            <p className="mt-4 text-xs font-bold uppercase tracking-widest text-gray-400">
              AI Report
            </p>

            <p className="mt-2 text-xl font-bold text-gray-950">
              {status === "completed" ? "Ready" : "Pending"}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Shakti Motion Intelligence™ analysis
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-3xl border border-gray-200 bg-white p-6">
          <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-gray-400">
            Session Notes
          </p>

          <p className="mt-3 text-sm leading-7 text-gray-600">
            {performance.notes || "No additional notes were added."}
          </p>
        </div>

        <div className="mt-6 rounded-3xl border border-orange-200 bg-[#FFF8F3] p-6">
          <p className="text-sm font-bold text-gray-950">
            Shakti Motion Intelligence™
          </p>

          <p className="mt-2 text-sm leading-6 text-gray-600">
            Biomechanical metrics, movement insights, performance scoring, and
            coaching recommendations will appear here when the analysis is
            completed.
          </p>
        </div>
      </div>
    </div>
  );
}