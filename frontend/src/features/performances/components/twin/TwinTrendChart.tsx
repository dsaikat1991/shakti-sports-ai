import { AlertTriangle } from "lucide-react";
import type { TwinMetricTrend } from "../../lib/twinEngine";
import { MetricTrendChart, type MetricTrendPoint } from "../../lib/readinessTrend";

const DIRECTION_LABEL: Record<string, string> = {
  improving: "Improving",
  regressing: "Regressing",
  stable: "Stable",
  high_variability: "High variability",
  insufficient_data: "Not enough data yet",
};

const DIRECTION_CLASS: Record<string, string> = {
  improving: "bg-green-100 text-green-700",
  regressing: "bg-red-100 text-red-700",
  stable: "bg-gray-100 text-gray-600",
  high_variability: "bg-amber-100 text-amber-700",
  insufficient_data: "bg-gray-100 text-gray-400",
};

// One metric's trend card - the honest "Not enough data yet" state
// (Step 4/14) lives here, scoped to this single metric, not the whole
// page. Experimental metrics (ground contact / duty factor / flight
// time) render with a persistent warning and never claim a direction as
// trustworthy, even if the underlying math produced one.
export default function TwinTrendChart({ twinTrend }: { twinTrend: TwinMetricTrend }) {
  const { metric, trend, points, excludedByProvider } = twinTrend;
  const isExperimental = metric.status === "experimental";

  if (trend.samples < 2) {
    return (
      <div className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-gray-950">{metric.label}</h3>
          {isExperimental && (
            <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-700">
              Experimental
            </span>
          )}
        </div>
        <p className="mt-3 text-sm text-gray-500">
          Not enough data yet - {metric.label.toLowerCase()} needs at least 2 analysed sessions to
          show a trend ({trend.samples} so far).
        </p>
      </div>
    );
  }

  const chartPoints: MetricTrendPoint[] = points.map((p) => ({
    label: p.recordedAt,
    value: p.value,
    date: p.recordedAt,
  }));

  return (
    <div className={`rounded-3xl border p-5 shadow-sm ${isExperimental ? "border-amber-200 bg-amber-50/30" : "border-gray-200 bg-white"}`}>
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-gray-950">{metric.label}</h3>
        <div className="flex items-center gap-2">
          {isExperimental && (
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-700">
              <AlertTriangle className="h-3 w-3" />
              Experimental
            </span>
          )}
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${DIRECTION_CLASS[trend.direction]}`}>
            {DIRECTION_LABEL[trend.direction]}
          </span>
        </div>
      </div>

      {metric.limitationText && (
        <p className="mt-2 text-xs leading-5 text-amber-700">{metric.limitationText}</p>
      )}

      <MetricTrendChart points={chartPoints} format={(v) => metric.format({ value: v })} />

      {excludedByProvider > 0 && (
        <p className="mt-3 text-xs text-gray-400">
          {excludedByProvider} earlier session{excludedByProvider === 1 ? "" : "s"} used a different
          analysis pipeline and {excludedByProvider === 1 ? "is" : "are"} excluded from this trend.
        </p>
      )}
    </div>
  );
}
