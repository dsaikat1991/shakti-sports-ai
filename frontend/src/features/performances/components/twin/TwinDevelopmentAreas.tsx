import { ClipboardList } from "lucide-react";
import EmptyState from "../../../../components/shared/EmptyState";
import type { TwinObservation } from "../../lib/twinEngine";

// Step 6 - every entry here comes straight from deriveDevelopmentAreas()
// (twinEngine.ts). These are observations ("recording quality
// inconsistent"), not coaching advice - the copy deliberately never
// prescribes what to do about it.
export default function TwinDevelopmentAreas({ areas }: { areas: TwinObservation[] }) {
  if (areas.length === 0) {
    return (
      <EmptyState
        icon={ClipboardList}
        tone="neutral"
        title="No development areas flagged yet"
        description="Development areas surface when a metric shows real variability or a slow decline across at least two analysed sessions."
      />
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {areas.map((item) => (
        <div key={item.key} className="rounded-3xl border border-amber-200 bg-amber-50 p-5">
          <div className="flex items-center gap-2">
            <ClipboardList className="h-4 w-4 text-amber-700" />
            <p className="font-bold text-amber-900">{item.label}</p>
          </div>
          <p className="mt-2 text-sm leading-6 text-amber-800">{item.detail}</p>
          <span className="mt-3 inline-block text-xs font-semibold uppercase tracking-wide text-amber-600">
            {item.category === "recording_quality" ? "Recording Quality" : "Athletic Performance"}
          </span>
        </div>
      ))}
    </div>
  );
}
