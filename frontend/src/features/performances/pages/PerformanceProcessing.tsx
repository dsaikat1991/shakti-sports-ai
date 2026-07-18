import { AlertTriangle, CheckCircle2, Clock3, Loader2, RefreshCw } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useState } from "react";

import { ROUTES } from "../../../constants/routes";
import { friendlyErrorMessage } from "../../../lib/friendlyError";
import { buildPerformanceDisplayName } from "../lib/performanceDisplayName";
import { usePerformance } from "../hooks/usePerformance";
import { useAnalysisPolling } from "../hooks/useAnalysisPolling";
import { useRetryAnalysis } from "../hooks/useRetryAnalysis";

const analysisQuotes = [
  "Every great performance starts with a single movement.",
  "Precision creates performance.",
  "Champions are built one repetition at a time.",
  "Train smarter. Compete stronger.",
];

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    const first = events[0] as { name?: string } | undefined;
    return first?.name ?? "Performance";
  }

  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }

  return "Performance";
}

// One explicit state machine instead of scattered booleans, so every
// state this page can actually be in has exactly one representation.
export type ProcessingState =
  | "queued"
  | "processing"
  | "completed"
  | "failed"
  | "timed_out"
  | "not_started";

export function deriveState(
  uploadStatus: string | null | undefined,
  jobStatus: string | undefined,
  timedOut: boolean,
): ProcessingState {
  if (uploadStatus === "completed" || jobStatus === "completed") {
    return "completed";
  }
  if (uploadStatus === "failed" || jobStatus === "failed") {
    return "failed";
  }
  if (timedOut) {
    return "timed_out";
  }
  if (jobStatus === "processing") {
    return "processing";
  }
  if (jobStatus === "queued") {
    return "queued";
  }
  // upload_status is "analyzing" (a job id exists) but we haven't heard
  // back from the backend on this poll cycle yet.
  return "not_started";
}

export default function PerformanceProcessing() {
  const { performanceId } = useParams();

  const { data, isLoading, error } = usePerformance(performanceId);

  const jobId =
    data?.analysis_job_id &&
    data?.upload_status !== "completed" &&
    data?.upload_status !== "failed"
      ? (data.analysis_job_id as string)
      : undefined;

  const job = useAnalysisPolling(performanceId, jobId);
  const retryAnalysis = useRetryAnalysis();

  // A single quote for the wait, not a fake step-by-step progress display -
  // the backend only reports queued/processing/completed/failed, nothing
  // finer-grained, so pretending to know "which step" it's on would be
  // exactly the kind of invented certainty this platform avoids.
  const [quote] = useState(
    () => analysisQuotes[Math.floor(Math.random() * analysisQuotes.length)],
  );

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-2xl shadow-gray-200/70">
        <Loader2 className="mx-auto h-10 w-10 animate-spin text-[#F0600E]" />

        <p className="mt-5 text-sm font-bold text-gray-600">
          Loading performance...
        </p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="mx-auto max-w-3xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center">
        <h1 className="text-2xl font-bold text-red-700">
          Unable to load this performance.
        </h1>

        <Link
          to={ROUTES.ATHLETE.HOME}
          className="mt-8 inline-flex rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white"
        >
          Go to Dashboard
        </Link>
      </div>
    );
  }

  const state = deriveState(data.upload_status, job.data?.status, job.timedOut);

  const failureReason =
    job.data?.error ??
    (data.analysis_error as string | null | undefined) ??
    "Analysis could not be completed.";

  const analysisNeverStarted = !data.analysis_job_id;

  function handleRetry() {
    if (!data || !data.video_url) return;
    retryAnalysis.retry({
      performanceId: data.id,
      videoPath: data.video_url as string,
    });
  }

  const isTerminal = state === "completed" || state === "failed";

  return (
    <div className="mx-auto max-w-3xl rounded-4xl border border-gray-200 bg-white px-8 py-6 text-center shadow-2xl shadow-gray-200/70">
      <div
        className={`mx-auto flex h-12 w-12 items-center justify-center rounded-2xl ${
          state === "failed" || state === "timed_out"
            ? "bg-red-100 text-red-700"
            : state === "completed"
              ? "bg-green-100 text-green-700"
              : "bg-orange-100 text-[#F0600E]"
        }`}
      >
        {state === "failed" || state === "timed_out" ? (
          <AlertTriangle className="h-6 w-6" />
        ) : state === "completed" ? (
          <CheckCircle2 className="h-6 w-6" />
        ) : (
          <Clock3 className="h-6 w-6" />
        )}
      </div>

      <p className="mt-4 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
        {state === "failed"
          ? "Analysis Failed"
          : state === "timed_out"
            ? "Taking Longer Than Expected"
            : state === "completed"
              ? "Analysis Complete"
              : "Upload Complete"}
      </p>

      <h1 className="mt-4 text-3xl font-bold leading-tight text-gray-950 md:text-4xl">
        {buildPerformanceDisplayName(data)}
      </h1>

      <div className="mx-auto mt-5 max-w-md rounded-3xl border border-gray-200 bg-gray-50 p-4">
        <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
          Session #
          {String(data.performance_number ?? 0).padStart(2, "0")}
        </p>

        <p className="mt-2 text-sm text-gray-500">
          {getEventName(data.events)} • {data.performance_date}
        </p>
      </div>

      {state === "failed" && (
        <>
          <p className="mx-auto mt-8 max-w-xl rounded-2xl bg-red-50 px-5 py-4 text-sm leading-6 text-red-700">
            {analysisNeverStarted
              ? "We couldn't start analyzing this recording. Your video is still saved, so nothing is lost - try again in a moment."
              : friendlyErrorMessage(new Error(failureReason), "analysis")}
          </p>

          {retryAnalysis.error && (
            <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-red-600">
              {friendlyErrorMessage(retryAnalysis.error, "analysis")}
            </p>
          )}
        </>
      )}

      {state === "timed_out" && (
        <p className="mx-auto mt-8 max-w-xl rounded-2xl bg-orange-50 px-5 py-4 text-sm leading-6 text-orange-800">
          This is taking much longer than usual. The analysis may still be
          running - check back later, or try again.
        </p>
      )}

      {state === "completed" && (
        <p className="mx-auto mt-8 max-w-xl text-base leading-7 text-gray-600">
          We've finished reading your performance. Your report is ready below.
        </p>
      )}

      {!isTerminal && state !== "timed_out" && (
        <>
          <p className="mx-auto mt-8 max-w-xl text-base leading-7 text-gray-600">
            We're reading your performance now. This usually takes a couple
            of minutes.
          </p>

          <div className="mx-auto mt-5 max-w-xl rounded-3xl p-6">
            <div className="flex items-center justify-center gap-3 text-sm font-bold text-gray-950">
              <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />

              {state === "queued" || state === "not_started"
                ? "Waiting in queue..."
                : "Analyzing your performance..."}
            </div>

            <p className="mx-auto mt-5 max-w-sm text-sm italic leading-6 text-gray-600">
              "{quote}"
            </p>
          </div>
        </>
      )}

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        {state === "completed" && (
          <Link
            to={ROUTES.ATHLETE.PERFORMANCE_REPORT(data.id)}
            className="rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
          >
            View Full Report
          </Link>
        )}

        {(state === "failed" || state === "timed_out") && (
          <button
            type="button"
            onClick={handleRetry}
            disabled={retryAnalysis.isPending}
            className="inline-flex items-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw
              className={`h-4 w-4 ${retryAnalysis.isPending ? "animate-spin" : ""}`}
            />
            {retryAnalysis.isPending ? "Retrying..." : "Retry Analysis"}
          </button>
        )}

        <Link
          to={ROUTES.ATHLETE.HOME}
          className="rounded-xl border border-gray-300 px-5 py-3 text-sm font-bold text-gray-800 transition hover:border-[#F0600E] hover:text-[#F0600E]"
        >
          Go to Dashboard
        </Link>

        <Link
          to={ROUTES.ATHLETE.NEW_PERFORMANCE}
          className="rounded-xl border border-gray-300 px-5 py-3 text-sm font-bold text-gray-800 transition hover:border-[#F0600E] hover:text-[#F0600E]"
        >
          + New Performance
        </Link>
      </div>
    </div>
  );
}
