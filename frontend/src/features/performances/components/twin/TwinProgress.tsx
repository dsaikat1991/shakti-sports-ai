import { AlertTriangle, Camera, Zap } from "lucide-react";
import { METRIC_REGISTRY } from "../../lib/metricRegistry";
import { buildTwinMetricTrend, type TwinSessionInput } from "../../lib/twinEngine";
import TwinTrendChart from "./TwinTrendChart";

// Step 4, Progress Engine - the three sections below are a deliberate,
// visible enforcement of the architecture's own rule (§08): athletic-
// performance trends and recording-quality trends are never rendered
// together as if they were the same kind of observation, and
// experimental (ground-contact-derived) metrics get their own
// permanently-labeled section, never mixed into the trusted ones.
export default function TwinProgress({ performances }: { performances: TwinSessionInput[] }) {
  const biomechanicsMetrics = METRIC_REGISTRY.filter(
    (m) => m.status === "production" && m.category === "biomechanics",
  );
  const recordingQualityMetrics = METRIC_REGISTRY.filter(
    (m) => m.status === "production" && m.category === "recording_quality",
  );
  const experimentalMetrics = METRIC_REGISTRY.filter((m) => m.status === "experimental");

  return (
    <div className="space-y-10">
      <section>
        <div className="mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-[#F0600E]" />
          <h2 className="font-['Anton'] text-2xl uppercase text-gray-950">Athletic Performance Trends</h2>
        </div>
        <p className="mb-4 text-sm text-gray-500">
          What the athlete's body is doing, session over session.
        </p>
        <div className="grid gap-4 md:grid-cols-2">
          {biomechanicsMetrics.map((metric) => (
            <TwinTrendChart key={metric.key} twinTrend={buildTwinMetricTrend(performances, metric)} />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center gap-2">
          <Camera className="h-5 w-5 text-[#2f5a6b]" />
          <h2 className="font-['Anton'] text-2xl uppercase text-gray-950">Recording Quality Trends</h2>
        </div>
        <p className="mb-4 text-sm text-gray-500">
          How well sessions were captured on camera - not an athletic performance signal. A rising
          trend here means recordings are getting more consistent, not that the athlete is improving.
        </p>
        <div className="grid gap-4 md:grid-cols-2">
          {recordingQualityMetrics.map((metric) => (
            <TwinTrendChart key={metric.key} twinTrend={buildTwinMetricTrend(performances, metric)} />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <h2 className="font-['Anton'] text-2xl uppercase text-gray-950">Experimental Metrics</h2>
        </div>
        <p className="mb-4 text-sm leading-6 text-gray-500">
          Ground-contact detection is confirmed unreliable for some camera angles. These are shown for
          reference only - never used to generate a strength, a development area, a personal best, or
          this Twin's confidence score.
        </p>
        <div className="grid gap-4 md:grid-cols-2">
          {experimentalMetrics.map((metric) => (
            <TwinTrendChart key={metric.key} twinTrend={buildTwinMetricTrend(performances, metric)} />
          ))}
        </div>
      </section>
    </div>
  );
}
