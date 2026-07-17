import type { AnalysisResult } from "../types/analysis";

// Shared by both comparison views (athlete-to-athlete and one-athlete-
// over-time) - a single registry so a future metric (Performance Index,
// AI Potential Score, benchmark rankings) is one new entry here, not a
// parallel implementation in each view. Lives under features/performances
// (not features/partners or features/athlete) deliberately - it's a
// neutral, analysis-result-shaped concern both features already depend
// on (AnalysisResult, RatingBadge), avoiding a coach-console -> athlete-
// console dependency direction that would couple coach permissions to
// athlete-page implementation details.
export interface ExtractedMetric {
  value: number;
  // Only set where the underlying data itself carries a per-metric
  // coverage/confidence figure (e.g. joint angle coverage_percent).
  // Absent (not zero) means "not applicable," not "unknown."
  coveragePercent?: number;
}

export type MetricStatus = "production" | "experimental";

export interface MetricDefinition {
  key: string;
  label: string;
  unit: string;
  category: "recording_quality" | "biomechanics";
  // Which event(s) this metric is meaningful for. Every metric here is
  // sprint-specific today because only sprint biomechanics has been
  // built/validated at all (see docs/ENGINEERING_HANDOFF.md §1) - this
  // field exists so a future hurdles/long-jump/high-jump metric doesn't
  // get silently compared against a sprint one.
  applicableEvents: string[];
  // "production": cross-validated against real footage and trusted for
  // comparison (see §9's bug fixes). "experimental": ground-contact-
  // derived metrics that a direct, quantified counterexample (§10.1)
  // proved cannot currently be trusted to separate true contacts from
  // swing-phase false positives - shown, never used to declare a
  // winner, always paired with limitationText in the UI.
  status: MetricStatus;
  limitationText?: string;
  // Below this, a value exists but is unreliable enough that the
  // comparability gate should treat it as unusable for this pair.
  minCoveragePercent?: number;
  accessor: (result: AnalysisResult) => ExtractedMetric | null;
  format: (metric: ExtractedMetric) => string;
}

function firstCompletedSegment(result: AnalysisResult): any | null {
  const biomechanics = result.biomechanics as any;
  if (biomechanics?.status === "skipped") return null;
  const segments = Array.isArray(biomechanics?.segments) ? biomechanics.segments : [];
  return segments.find((s: any) => s?.status !== "skipped") ?? null;
}

// One metric entry per joint, reading mean_degrees + coverage_percent
// from segment.joint_angles[jointKey] (same nested shape rendered in
// PerformanceDetail.tsx's per-segment joint-angle table). Joint angle
// calculation itself isn't flagged unreliable anywhere in this codebase
// (only the general "projected 2D, not true 3D" limitation applies,
// same as every other angle in this report) - production status, but
// gated on a real per-joint coverage threshold so a joint that was only
// visible in a handful of frames doesn't quietly feed a trend/strength.
const JOINT_ANGLE_DEFINITIONS: { key: string; label: string }[] = [
  { key: "left_knee", label: "Left Knee Angle" },
  { key: "right_knee", label: "Right Knee Angle" },
  { key: "left_hip", label: "Left Hip Angle" },
  { key: "right_hip", label: "Right Hip Angle" },
  { key: "left_elbow", label: "Left Elbow Angle" },
  { key: "right_elbow", label: "Right Elbow Angle" },
];

function buildJointAngleMetrics(): MetricDefinition[] {
  return JOINT_ANGLE_DEFINITIONS.map(({ key, label }) => ({
    key: `joint_angle_${key}`,
    label,
    unit: "deg",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "production",
    minCoveragePercent: 60,
    accessor: (result: AnalysisResult) => {
      const segment = firstCompletedSegment(result);
      const joint = segment?.joint_angles?.[key];
      const value = joint?.mean_degrees;
      if (typeof value !== "number") return null;
      return {
        value,
        coveragePercent:
          typeof joint?.coverage_percent === "number" ? joint.coverage_percent : undefined,
      };
    },
    format: (m: ExtractedMetric) => `${Math.round(m.value)}°`,
  }));
}

export const METRIC_REGISTRY: MetricDefinition[] = [
  {
    key: "detection_rate",
    label: "Detection Rate",
    unit: "%",
    category: "recording_quality",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    accessor: (result) => {
      const value = result.analysis?.detection_rate_percent;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}%`,
  },
  {
    key: "readiness_score",
    label: "Recording Readiness Score",
    unit: "/100",
    category: "recording_quality",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    limitationText:
      "Reflects whether the recording was captured well enough to analyze - not an athletic performance score. Do not read a higher number here as \"a better athlete.\"",
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.analysis_readiness?.score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}/100`,
  },
  {
    key: "cadence",
    label: "Cadence",
    unit: "steps/min",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "production",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.cadence?.steps_per_minute;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)} steps/min`,
  },
  {
    key: "stride_frequency",
    label: "Stride Frequency",
    unit: "Hz",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "production",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.stride?.stride_frequency_hz;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${m.value.toFixed(2)} Hz`,
  },
  {
    key: "knee_symmetry",
    label: "Knee Symmetry",
    unit: "%",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "production",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.knee_symmetry_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}%`,
  },
  {
    key: "body_visibility",
    label: "Body Visibility",
    unit: "%",
    // Categorized recording_quality, not biomechanics, deliberately -
    // this measures whether the CAMERA captured the athlete's full body
    // well, not what the athlete's body is doing. The Digital Twin must
    // never present a rising trend here as "the athlete improved" (see
    // docs/ENGINEERING_HANDOFF.md, Digital Twin architecture proposal).
    category: "recording_quality",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.metrics?.full_body_visibility_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}%`,
  },
  {
    key: "movement_quality",
    label: "Movement Quality",
    unit: "/100",
    // Same reasoning as body_visibility above - this is the quality
    // gate's athlete_movement_score (how much genuine athletic motion
    // was detected on camera, used to reject a standing-pose recording),
    // not a judgment of athletic ability. recording_quality category.
    category: "recording_quality",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.metrics?.athlete_movement_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}/100`,
  },
  {
    key: "ground_contacts",
    label: "Ground Contacts",
    unit: "detected",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "experimental",
    limitationText:
      "Ground-contact detection is confirmed unreliable for some camera angles - a hand-labeled counterexample showed a true contact scoring lower on the only signal this detector uses than a confirmed false positive. Not a trustworthy selection criterion yet.",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.ground_contact?.events;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)} detected`,
  },
  {
    key: "duty_factor",
    label: "Duty Factor",
    unit: "%",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "experimental",
    limitationText: "Derived from ground-contact detection - inherits the same unreliability.",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.duty_factor_percent;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${m.value.toFixed(1)}%`,
  },
  {
    key: "flight_time",
    label: "Flight Time",
    unit: "ms",
    category: "biomechanics",
    applicableEvents: ["Sprint"],
    status: "experimental",
    limitationText: "Derived from ground-contact detection - inherits the same unreliability.",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.flight_time?.median_flight_time_ms;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)} ms`,
  },
  ...buildJointAngleMetrics(),
];

export function getEventName(events: unknown): string {
  if (Array.isArray(events)) {
    return (events[0] as { name?: string } | undefined)?.name ?? "Performance";
  }
  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }
  return "Performance";
}

export interface ComparabilityResult {
  comparable: boolean;
  reason?: string;
}

// Global (pair-level) comparability - checked once per pair, before any
// per-metric comparison. Deliberately conservative: only sprint has any
// validated biomechanics at all (§1), so a mismatched event or an
// incomplete analysis blocks comparison outright rather than showing a
// partial, possibly-misleading comparison.
export function checkPairComparability(
  eventA: string,
  eventB: string,
  resultA: AnalysisResult,
  resultB: AnalysisResult,
): ComparabilityResult {
  if (eventA !== eventB) {
    return { comparable: false, reason: `Different events (${eventA} vs ${eventB}) - not comparable.` };
  }

  if (resultA.provider !== resultB.provider) {
    return {
      comparable: false,
      reason: `Generated by different pose-estimation pipelines (${resultA.provider} vs ${resultB.provider}) - no algorithm-version field exists yet to confirm these are comparable, so they're treated as not comparable rather than assumed compatible.`,
    };
  }

  return { comparable: true };
}

// Per-metric comparability - even when the pair overall is comparable,
// an individual metric may not be (missing on one side, or below its
// trustable coverage threshold).
export function checkMetricComparability(
  metric: MetricDefinition,
  eventName: string,
  a: ExtractedMetric | null,
  b: ExtractedMetric | null,
): ComparabilityResult {
  if (!metric.applicableEvents.includes(eventName)) {
    return { comparable: false, reason: `Not applicable to ${eventName}.` };
  }
  if (!a || !b) {
    return { comparable: false, reason: "Missing on at least one side." };
  }
  if (
    metric.minCoveragePercent !== undefined &&
    ((a.coveragePercent !== undefined && a.coveragePercent < metric.minCoveragePercent) ||
      (b.coveragePercent !== undefined && b.coveragePercent < metric.minCoveragePercent))
  ) {
    return { comparable: false, reason: "Coverage too low to trust on at least one side." };
  }
  return { comparable: true };
}
