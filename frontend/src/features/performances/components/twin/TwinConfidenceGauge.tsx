import type { TwinConfidence } from "../../lib/twinEngine";

const LEVEL_COPY: Record<TwinConfidence["level"], { label: string; color: string }> = {
  high: { label: "High Confidence", color: "#16a34a" },
  medium: { label: "Medium Confidence", color: "#d97706" },
  low: { label: "Low Confidence", color: "#dc2626" },
};

// Same radial-gauge visual language as PerformanceDetail.tsx's
// ScoreGauge (module-private there) - rebuilt here as its own Twin*
// component per the component model, not imported, so this becomes
// independently reusable in Coach/Academy contexts later without
// depending on a page-specific internal.
export default function TwinConfidenceGauge({ confidence }: { confidence: TwinConfidence | null }) {
  if (!confidence) {
    return (
      <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-5 text-center">
        <p className="text-sm font-semibold text-gray-500">No Twin yet</p>
        <p className="mt-1 text-xs text-gray-400">Complete an analysis to see your Twin confidence.</p>
      </div>
    );
  }

  const clamped = Math.min(100, Math.max(0, confidence.score));
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped / 100);
  const { label, color } = LEVEL_COPY[confidence.level];

  return (
    <div className="flex items-center gap-4">
      <div className="relative h-24 w-24 shrink-0">
        <svg width="96" height="96" viewBox="0 0 96 96" className="-rotate-90">
          <circle cx="48" cy="48" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="8" />
          <circle
            cx="48"
            cy="48"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="text-2xl font-black text-gray-950">{Math.round(clamped)}</p>
          <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">/100</p>
        </div>
      </div>
      <div>
        <p className="text-xs font-bold uppercase tracking-widest text-gray-400">Twin Confidence</p>
        <p className="mt-1 text-lg font-bold" style={{ color }}>
          {label}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          {confidence.sessionCount} analysed session{confidence.sessionCount === 1 ? "" : "s"}
        </p>
      </div>
    </div>
  );
}
