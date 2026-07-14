import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import { ROUTES } from "../../../constants/routes";
import { usePerformance } from "../hooks/usePerformance";
import { useAnalysisPolling } from "../hooks/useAnalysisPolling";

const processingSteps = [
  "Waiting in queue...",
  "Detecting athlete...",
  "Tracking body landmarks...",
  "Analyzing biomechanics...",
  "Preparing performance report...",
];

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

  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setStepIndex((current) =>
        current >= processingSteps.length - 1 ? current : current + 1,
      );
    }, 2500);

    return () => window.clearInterval(interval);
  }, []);

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

  // A completed/failed job is either already reflected on the Supabase row
  // (data.upload_status), or was just detected live by the poll (job.data) -
  // check both so the UI updates the instant the backend finishes, without
  // waiting for the Supabase write + refetch round trip.
  const isCompleted =
    data.upload_status === "completed" || job.data?.status === "completed";

  const isFailed =
    data.upload_status === "failed" || job.data?.status === "failed";

  const failureReason =
    job.data?.error ??
    (data.analysis_error as string | null | undefined) ??
    "Analysis could not be completed.";

  const analysisNeverStarted =
    !data.analysis_job_id && data.upload_status !== "completed";

  const quote = analysisQuotes[stepIndex % analysisQuotes.length];

  return (
    <div className="mx-auto max-w-3xl rounded-4xl border border-gray-200 bg-white px-8 py-6 text-center shadow-2xl shadow-gray-200/70">
      <div
        className={`mx-auto flex h-12 w-12 items-center justify-center rounded-2xl ${
          isFailed
            ? "bg-red-100 text-red-700"
            : "bg-green-100 text-green-700"
        }`}
      >
        {isFailed ? (
          <AlertTriangle className="h-6 w-6" />
        ) : (
          <CheckCircle2 className="h-6 w-6" />
        )}
      </div>

      <p className="mt-4 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
        {isFailed ? "Analysis Failed" : isCompleted ? "Analysis Complete" : "Upload Complete"}
      </p>

      <h1 className="mt-4 font-['Anton'] text-4xl md:text-5xl uppercase leading-none text-gray-950">
        {data.title}
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

      {isFailed && (
        <>
          <p className="mx-auto mt-8 max-w-xl rounded-2xl bg-red-50 px-5 py-4 text-sm leading-6 text-red-700">
            {failureReason}
          </p>

          {analysisNeverStarted && (
            <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-gray-500">
              This usually means the analysis backend wasn't reachable when
              this recording was uploaded. Your video is still saved.
            </p>
          )}
        </>
      )}

      {isCompleted && !isFailed && (
        <p className="mx-auto mt-8 max-w-xl text-base leading-7 text-gray-600">
          Shakti Motion Intelligence™ has finished analyzing your
          performance. Your biomechanical report is ready.
        </p>
      )}

      {!isCompleted && !isFailed && (
        <>
          <p className="mx-auto mt-8 max-w-xl text-base leading-7 text-gray-600">
            Shakti Motion Intelligence™ is analyzing your performance to
            generate personalized biomechanical insights and coaching
            recommendations.
          </p>

          <div className="mx-auto mt-5 max-w-xl rounded-3xl p-6">
            <div className="flex items-center justify-center gap-3 text-sm font-bold text-gray-950">
              <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />

              {job.data?.status === "queued"
                ? "Waiting in queue..."
                : processingSteps[stepIndex]}
            </div>

            <p className="mx-auto mt-5 max-w-sm text-sm italic leading-6 text-gray-600">
              "{quote}"
            </p>
          </div>
        </>
      )}

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        {isCompleted && !isFailed && (
          <Link
            to={ROUTES.ATHLETE.PERFORMANCE_REPORT(data.id)}
            className="rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
          >
            View Full Report
          </Link>
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
