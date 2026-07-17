import { Minus, TrendingDown, TrendingUp, AlertTriangle } from "lucide-react";
import type { TrendDirection } from "../../lib/twinEngine";

const DIRECTION_ICON: Record<TrendDirection, typeof TrendingUp> = {
  improving: TrendingUp,
  regressing: TrendingDown,
  stable: Minus,
  high_variability: AlertTriangle,
  insufficient_data: Minus,
};

const DIRECTION_COLOR: Record<TrendDirection, string> = {
  improving: "text-green-700",
  regressing: "text-red-600",
  stable: "text-gray-500",
  high_variability: "text-amber-600",
  insufficient_data: "text-gray-300",
};

// Generic single-metric card - value, unit, and a trend-direction
// indicator. Used across TwinProgress, TwinConsistency, and
// TwinPersonalBests rather than each building its own card markup.
export default function TwinMetricCard({
  label,
  value,
  direction,
  caveat,
}: {
  label: string;
  value: string;
  direction?: TrendDirection;
  caveat?: string;
}) {
  const Icon = direction ? DIRECTION_ICON[direction] : null;

  return (
    <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs font-bold uppercase tracking-widest text-gray-400">{label}</p>
        {Icon && direction && <Icon className={`h-4 w-4 ${DIRECTION_COLOR[direction]}`} />}
      </div>
      <p className="mt-1 text-lg font-bold text-gray-950">{value}</p>
      {caveat && <p className="mt-1 text-xs text-amber-600">{caveat}</p>}
    </div>
  );
}
