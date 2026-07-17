import { Sparkles } from "lucide-react";
import EmptyState from "../../../../components/shared/EmptyState";
import type { TwinObservation } from "../../lib/twinEngine";

// Step 5 - every entry here comes straight from deriveStrengths()
// (twinEngine.ts), a deterministic rule over already-computed trends.
// Nothing here is generated text.
export default function TwinStrengths({ strengths }: { strengths: TwinObservation[] }) {
  if (strengths.length === 0) {
    return (
      <EmptyState
        icon={Sparkles}
        tone="neutral"
        title="No strengths identified yet"
        description="Strengths are derived from stable or improving metrics across at least two analysed sessions - keep uploading to build this out."
      />
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {strengths.map((item) => (
        <div key={item.key} className="rounded-3xl border border-green-200 bg-green-50 p-5">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-green-700" />
            <p className="font-bold text-green-900">{item.label}</p>
          </div>
          <p className="mt-2 text-sm leading-6 text-green-800">{item.detail}</p>
          <span className="mt-3 inline-block text-xs font-semibold uppercase tracking-wide text-green-600">
            {item.category === "recording_quality" ? "Recording Quality" : "Athletic Performance"}
          </span>
        </div>
      ))}
    </div>
  );
}
