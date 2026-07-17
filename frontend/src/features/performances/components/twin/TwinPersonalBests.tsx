import { Trophy } from "lucide-react";
import { Link } from "react-router-dom";
import EmptyState from "../../../../components/shared/EmptyState";
import { formatSessionDate } from "../../lib/analysisSummary";
import type { PersonalBestResult } from "../../lib/twinEngine";

export interface TwinPersonalBestItem extends PersonalBestResult {
  label: string;
  unit: string;
  reportHref: string;
}

// Step 8 - every PB links back to the originating performance (via
// reportHref, resolved by the assembly page from performanceId). Only
// production-status metrics are eligible (enforced in
// buildTwinPersonalBests, twinEngine.ts) - a personal best is never
// derived from ground contact, duty factor, or flight time while that
// detector remains unvalidated.
export default function TwinPersonalBests({ items }: { items: TwinPersonalBestItem[] }) {
  if (items.length === 0) {
    return (
      <EmptyState
        icon={Trophy}
        tone="neutral"
        title="No personal bests yet"
        description="Complete an analysis to start tracking your best sessions."
      />
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <Link
          key={item.metricKey}
          to={item.reportHref}
          className="group rounded-3xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-lg"
        >
          <div className="flex items-center gap-2">
            <Trophy className="h-4 w-4 text-[#F0600E]" />
            <p className="text-xs font-bold uppercase tracking-widest text-gray-400">{item.label}</p>
          </div>
          <p className="mt-2 text-2xl font-black text-gray-950">
            {item.value.toFixed(item.unit === "Hz" ? 2 : 0)}
            <span className="ml-1 text-sm font-semibold text-gray-400">{item.unit}</span>
          </p>
          <p className="mt-1 text-xs text-gray-400">{formatSessionDate(item.recordedAt)}</p>
        </Link>
      ))}
    </div>
  );
}
