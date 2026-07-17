// Generic bar-chart trend primitive, normalizing to the actual min/max
// of the point set rather than assuming a fixed 0-100 scale, since most
// biomechanics metrics don't have one. Shared by TwinTrendChart.tsx -
// the metric-specific trend-building logic lives in twinEngine.ts
// (buildTwinMetricTrend), not here.

export interface MetricTrendPoint {
  label: string;
  value: number;
  date: string;
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
