import { CheckCircle2, Loader2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";

import { ROUTES } from "../../../constants/routes";
import { usePerformance } from "../hooks/usePerformance";

const analysisSteps = [
  "Receiving recording...",
  "Detecting athlete...",
  "Tracking body landmarks...",
  "Analyzing biomechanics...",
  "Generating AI insights...",
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

function statusLabel(status: string | null) {
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

export default function PerformanceProcessing() {
  const { performanceId } = useParams();

  const { data, isLoading, error } = usePerformance(performanceId);

  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setStepIndex((current) => {
        if (current >= analysisSteps.length - 1) {
          return current;
        }

        return current + 1;
      });
    }, 2500);

    return () => window.clearInterval(interval);
  }, []);

  const progress = useMemo(() => {
    return Math.round(
      ((stepIndex + 1) / analysisSteps.length) * 100,
    );
  }, [stepIndex]);

  const quote =
    analysisQuotes[stepIndex % analysisQuotes.length];

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

  return (
    <div className="mx-auto max-w-3xl rounded-4xl border border-gray-200 bg-white px-8 py-6 text-center shadow-2xl shadow-gray-200/70">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-green-100 text-green-700">
        <CheckCircle2 className="h-6 w-6" />
      </div>

      <p className="mt-4 font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.22em] text-[#F0600E]">
        Upload Complete
      </p>

      <h1 className="mt-4 font-['Anton'] text-4xl md:text-5xl uppercase leading-none text-gray-950">
        Performance Uploaded
      </h1>

      <div className="mx-auto mt-5 max-w-md rounded-3xl border border-gray-200 bg-gray-50 p-4">
        <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
          Session #
          {String(data.performance_number ?? 0).padStart(2, "0")}
        </p>

        <h2 className="mt-2 text-2xl font-bold text-gray-950">
          {data.title}
        </h2>

        <p className="mt-2 text-sm text-gray-500">
          {getEventName(data.events)} •{" "}
          {statusLabel(data.upload_status)}
        </p>

        <p className="mt-1 text-sm text-gray-400">
          {data.performance_date}
        </p>
      </div>

      <p className="mx-auto mt-8 max-w-xl text-base leading-7 text-gray-600">
        Shakti Motion Intelligence™ is analyzing your performance to
        generate personalized biomechanical insights and coaching
        recommendations.
      </p>

      <div className="mx-auto mt-5 max-w-xl rounded-3xl p-6">
        <div className="flex items-center justify-center gap-3 text-sm font-bold text-gray-950">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />

          {analysisSteps[stepIndex]}
        </div>

        <div className="mt-6 h-2 overflow-hidden rounded-full bg-orange-100">
          <div
            className="h-full rounded-full bg-[#F0600E] transition-all duration-700"
            style={{
              width: `${progress}%`,
            }}
          />
        </div>

        <p className="mt-3 font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
          {progress}% Complete
        </p>

        <p className="mx-auto mt-5 max-w-sm text-sm italic leading-6 text-gray-600">
          "{quote}"
        </p>
      </div>

      <div className="mt-6 flex flex-wrap justify-center gap-3">
        <Link
          to={ROUTES.ATHLETE.HOME}
          className="rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
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