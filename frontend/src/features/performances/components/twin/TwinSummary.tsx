import { Trophy } from "lucide-react";
import { formatSessionDate } from "../../lib/analysisSummary";
import TwinConfidenceGauge from "./TwinConfidenceGauge";
import type { TwinConfidence } from "../../lib/twinEngine";

export interface TwinSummaryProps {
  athleteName: string;
  eventName: string | null;
  developmentStageLabel: string;
  sessionCount: number;
  latestAnalysisDate: string | null;
  personalBestLabel: string | null;
  confidence: TwinConfidence | null;
}

// The Twin's identity header - "who am I as an athlete today," answered
// entirely from real, already-stored data (event, session count, latest
// analysis date, the athlete's own recorded personal best) plus the
// data-maturity-based development stage. No generated narrative text.
export default function TwinSummary({
  athleteName,
  eventName,
  developmentStageLabel,
  sessionCount,
  latestAnalysisDate,
  personalBestLabel,
  confidence,
}: TwinSummaryProps) {
  return (
    <div className="rounded-4xl border border-gray-200 bg-white p-7 shadow-xl shadow-gray-200/60 md:p-9">
      <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
        My Progress
      </p>
      <h1 className="mt-3 text-2xl font-bold leading-tight text-gray-950 md:text-3xl">
        {athleteName}
      </h1>
      <p className="mt-3 text-sm text-gray-500">
        {eventName ?? "Event not set"} · {developmentStageLabel}
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400">Sessions Analysed</p>
          <p className="mt-2 text-2xl font-bold text-gray-950">{sessionCount}</p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <p className="text-xs font-bold uppercase tracking-widest text-gray-400">Latest Analysis</p>
          <p className="mt-2 text-lg font-bold text-gray-950">
            {latestAnalysisDate ? formatSessionDate(latestAnalysisDate) : "None yet"}
          </p>
        </div>

        <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
          <div className="flex items-center gap-2">
            <Trophy className="h-4 w-4 text-[#F0600E]" />
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400">Personal Best</p>
          </div>
          <p className="mt-2 text-lg font-bold text-gray-950">{personalBestLabel ?? "Not set yet"}</p>
        </div>
      </div>

      <div className="mt-6 rounded-3xl border border-gray-200 bg-gray-50 p-5">
        <TwinConfidenceGauge confidence={confidence} />
      </div>
    </div>
  );
}
