import type { MetricDefinition } from "./metricRegistry";

// Extracted from AthleteProgress.tsx (Athlete Console) so both the
// athlete's own Progress page and a coach-side single-athlete view can
// reuse the exact same logic - no copy that could drift, and no
// coach-console -> athlete-console import direction (this lives in the
// neutral features/performances feature both already depend on).

export interface ReadinessPoint {
  label: string;
  score: number;
  date: string;
}

// Real, already-computed recording-quality readiness scores pulled
// straight from each session's analysis_result - deliberately not the
// same thing as a future athletic Performance Index (roadmap step 8,
// not built). This trend is about whether recordings are being
// captured well enough to analyze, not an athletic score.
export function buildReadinessTrend(performances: any[]): ReadinessPoint[] {
  return performances
    .map((performance) => {
      if (performance.upload_status !== "completed" || !performance.analysis_result) {
        return null;
      }

      const result = performance.analysis_result as any;
      const score = result?.recording_quality?.analysis_readiness?.score;

      if (typeof score !== "number") return null;

      return {
        label: `#${String(performance.performance_number ?? 0).padStart(2, "0")}`,
        score,
        date: performance.performance_date ?? performance.created_at,
      };
    })
    .filter((point): point is ReadinessPoint => point !== null)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
}

export function ReadinessTrendChart({ points }: { points: ReadinessPoint[] }) {
  if (points.length === 0) {
    return (
      <p className="mt-4 text-sm leading-6 text-gray-500">
        Analyze a session to start seeing a recording-readiness trend here.
      </p>
    );
  }

  const chartHeight = 96;

  return (
    <div className="mt-4">
      <div className="flex items-end gap-3" style={{ height: chartHeight }}>
        {points.map((point) => {
          const barHeight = Math.max(6, (Math.min(100, Math.max(0, point.score)) / 100) * chartHeight);
          const passed = point.score >= 70;

          return (
            <div key={point.label} className="flex flex-1 flex-col items-center justify-end gap-1">
              <span className="text-[11px] font-bold text-gray-500">
                {Math.round(point.score)}
              </span>
              <div
                className={`w-full max-w-10 rounded-t-md ${passed ? "bg-green-500" : "bg-red-400"}`}
                style={{ height: barHeight }}
              />
            </div>
          );
        })}
      </div>

      <div className="mt-2 flex gap-3">
        {points.map((point) => (
          <span
            key={point.label}
            className="flex-1 truncate text-center text-[11px] font-semibold text-gray-400"
          >
            {point.label}
          </span>
        ))}
      </div>
    </div>
  );
}

export interface MetricTrendPoint {
  label: string;
  value: number;
  date: string;
}

// Generic version of the above for any registry metric (cadence, knee
// symmetry, etc.) - normalizes bar heights to the actual min/max of the
// point set rather than assuming a fixed 0-100 scale, since most
// biomechanics metrics don't have one. No pass/fail coloring (unlike
// ReadinessTrendChart's 70-point threshold) because most metrics here
// don't have a single meaningful cutoff - this is a trend, not a gate.
export function buildMetricTrend(
  performances: any[],
  metric: MetricDefinition,
): MetricTrendPoint[] {
  return performances
    .map((performance) => {
      if (performance.upload_status !== "completed" || !performance.analysis_result) {
        return null;
      }

      const extracted = metric.accessor(performance.analysis_result);
      if (!extracted) return null;

      return {
        label: `#${String(performance.performance_number ?? 0).padStart(2, "0")}`,
        value: extracted.value,
        date: performance.performance_date ?? performance.created_at,
      };
    })
    .filter((point): point is MetricTrendPoint => point !== null)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
}

export function MetricTrendChart({
  points,
  format,
}: {
  points: MetricTrendPoint[];
  format: (value: number) => string;
}) {
  if (points.length === 0) {
    return <p className="mt-4 text-sm leading-6 text-gray-500">No completed sessions with this metric yet.</p>;
  }

  const chartHeight = 96;
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  return (
    <div className="mt-4">
      <div className="flex items-end gap-3" style={{ height: chartHeight }}>
        {points.map((point) => {
          const barHeight = Math.max(6, ((point.value - min) / range) * chartHeight * 0.85 + chartHeight * 0.15);

          return (
            <div key={point.label} className="flex flex-1 flex-col items-center justify-end gap-1">
              <span className="text-[11px] font-bold text-gray-500">{format(point.value)}</span>
              <div
                className="w-full max-w-10 rounded-t-md bg-[#F0600E]"
                style={{ height: barHeight }}
              />
            </div>
          );
        })}
      </div>

      <div className="mt-2 flex gap-3">
        {points.map((point) => (
          <span
            key={point.label}
            className="flex-1 truncate text-center text-[11px] font-semibold text-gray-400"
          >
            {point.label}
          </span>
        ))}
      </div>
    </div>
  );
}
