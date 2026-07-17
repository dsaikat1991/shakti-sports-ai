import EmptyState from "../../../../components/shared/EmptyState";
import { Repeat } from "lucide-react";
import type { ConsistencySummary } from "../../lib/twinEngine";
import TwinMetricCard from "./TwinMetricCard";

// Step 7. Twin confidence itself (the "AI confidence" consistency
// example) is already shown prominently in TwinSummary/
// TwinConfidenceGauge - not duplicated here as a second widget.
export default function TwinConsistency({ consistency }: { consistency: ConsistencySummary }) {
  if (consistency.sampleSize < 2) {
    return (
      <EmptyState
        icon={Repeat}
        tone="neutral"
        title="Not enough data yet"
        description="Consistency is computed from at least two analysed sessions."
      />
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <TwinMetricCard
        label="Upload Frequency"
        value={
          consistency.uploadFrequencyDays !== null
            ? `Every ${Math.round(consistency.uploadFrequencyDays)} days`
            : "N/A"
        }
      />
      <TwinMetricCard
        label="Session Completion"
        value={
          consistency.sessionCompletionRatePercent !== null
            ? `${Math.round(consistency.sessionCompletionRatePercent)}%`
            : "N/A"
        }
      />
      <TwinMetricCard
        label="Recording Consistency"
        value={
          consistency.recordingConsistencyCvPercent !== null
            ? `${consistency.recordingConsistencyCvPercent.toFixed(1)}% variation`
            : "N/A"
        }
        caveat="Lower is more consistent"
      />
      <TwinMetricCard
        label="Metric Stability"
        value={
          consistency.metricStabilityCvPercent !== null
            ? `${consistency.metricStabilityCvPercent.toFixed(1)}% variation`
            : "N/A"
        }
        caveat="Average across biomechanics metrics"
      />
    </div>
  );
}
