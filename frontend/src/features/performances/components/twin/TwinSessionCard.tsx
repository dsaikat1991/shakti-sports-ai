import { CalendarDays, CheckCircle2, ShieldAlert, StickyNote } from "lucide-react";
import { Link } from "react-router-dom";
import { formatSessionDate } from "../../lib/analysisSummary";
import type { AnalysisSummary } from "../../lib/analysisSummary";
import { RatingBadge } from "../../pages/PerformanceDetail";

export interface TwinSessionCardProps {
  performanceNumber: number;
  title: string;
  date: string;
  eventName: string;
  status: string | null;
  summary: AnalysisSummary | null;
  notes: string | null;
  reportHref: string;
}

// One node on the Digital Twin timeline (Step 3) - upload, analysis
// status, recording quality, biomechanics availability, and notes, all
// read directly from the performance row. Clicking through opens the
// existing, unmodified PerformanceDetail.tsx report - no second report
// renderer.
export default function TwinSessionCard({
  performanceNumber,
  title,
  date,
  eventName,
  status,
  summary,
  notes,
  reportHref,
}: TwinSessionCardProps) {
  return (
    <Link
      to={reportHref}
      className="group block rounded-3xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-orange-200 hover:shadow-lg"
    >
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.18em] text-[#F0600E]">
          #{String(performanceNumber).padStart(2, "0")}
        </p>
        {summary && <RatingBadge rating={summary.rating} />}
        {summary && (
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold ${
              summary.biomechanicsReady ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
            }`}
          >
            {summary.biomechanicsReady ? (
              <CheckCircle2 className="h-3 w-3" />
            ) : (
              <ShieldAlert className="h-3 w-3" />
            )}
            {summary.biomechanicsReady ? "Biomechanics available" : "Biomechanics skipped"}
          </span>
        )}
      </div>

      <h3 className="mt-2 text-lg font-bold text-gray-950">{title}</h3>
      <p className="mt-1 flex items-center gap-2 text-sm text-gray-500">
        <CalendarDays className="h-4 w-4" />
        {formatSessionDate(date)} · {eventName} · {status ?? "uploaded"}
      </p>

      {notes && (
        <p className="mt-2 flex items-start gap-2 text-sm leading-6 text-gray-600">
          <StickyNote className="mt-0.5 h-4 w-4 shrink-0 text-gray-400" />
          {notes}
        </p>
      )}
    </Link>
  );
}
