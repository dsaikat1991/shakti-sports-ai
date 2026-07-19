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
//
// This is the canonical Metric Registry (docs/ENGINEERING_HANDOFF.md §33):
// every current and future athlete-facing metric's comparison/trend
// semantics live HERE, once, as data - not re-derived or hardcoded in any
// consuming component. Two real bugs motivated this (§33): PartnerCompare
// highlighted a "winner" for every metric including joint angles (a bigger
// knee angle isn't "better"), and the Digital Twin's strengths/development-
// areas/personal-bests generated "Improving Left Knee Angle" text from the
// same non-directional metrics. Both are fixed by having every consumer
// read `comparisonMode` from here instead of assuming "higher is better."
export interface ExtractedMetric {
  value: number;
  // Only set where the underlying data itself carries a per-metric
  // coverage/confidence figure (e.g. joint angle coverage_percent).
  // Absent (not zero) means "not applicable," not "unknown."
  coveragePercent?: number;
}

export type MetricStatus = "production" | "experimental";

// How two values of this metric should be compared, if at all - the single
// source of truth every UI (Coach Console comparison, Digital Twin
// strengths/development-areas/personal-bests, any future comparison
// surface) must consult instead of assuming "higher is better."
//
// HIGHER_IS_BETTER / LOWER_IS_BETTER - an objective direction exists, OR
//   (cadence, stride frequency - see §33) a deliberate product-level
//   interpretation preserving existing shipped behavior, disclosed via
//   limitationText rather than asserted as validated sports science.
// TARGET_RANGE - there's an ideal band, not a direction (no current metric
//   uses this; reserved for a future metric with a documented ideal range -
//   not invented for cadence/stride frequency, since no such range has
//   ever been validated in this codebase - see §33).
// SYMMETRY - the metric already encodes "how close to balanced" as a
//   single higher-is-better score (e.g. knee_symmetry_score).
// NEUTRAL - the raw value has no validated better/worse direction at all
//   AND no existing product behavior already treats it as directional
//   (a joint angle has an ideal range dependent on many factors, not a
//   bigger-or-smaller-is-better reading, and nothing in the shipped
//   product ever ranked one - see §33).
// EXPERIMENTAL - the underlying detector is not yet trustworthy enough for
//   ANY comparison, regardless of what the raw direction would suggest.
// NOT_COMPARABLE - reserved for a future metric that is neither directional
//   nor a meaningful raw count (e.g. a categorical or ID-like value).
export type ComparisonMode =
  | "HIGHER_IS_BETTER"
  | "LOWER_IS_BETTER"
  | "TARGET_RANGE"
  | "SYMMETRY"
  | "NEUTRAL"
  | "EXPERIMENTAL"
  | "NOT_COMPARABLE";

// How a change in this metric's value over time should be framed - derived
// by default from comparisonMode (see deriveDefaultTrendMode below) but
// individually overridable per metric (see defineMetric's `trendMode`
// input), so the two usually agree without being forced to.
export type TrendMode = "INCREASING" | "DECREASING" | "MAINTAIN" | "NEUTRAL" | "UNKNOWN" | "EXPERIMENTAL";

export interface MetricDefinition {
  key: string;
  label: string;
  // Longer-form explanation than `label` - inert metadata today (not yet
  // rendered anywhere), for future documentation/tooling surfaces.
  description?: string;
  unit: string;
  category: "recording_quality" | "biomechanics";
  // Finer-grained grouping than category, e.g. "gait_timing", "joint_angle",
  // "tracking" - inert metadata today, for a future grouped-metrics UI.
  subcategory?: string;
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
  // winner, always paired with limitationText in the UI. This is the
  // pre-existing field name, unchanged (docs/ENGINEERING_HANDOFF.md §33 -
  // deliberately NOT renamed to "validationStatus" to avoid a repository-
  // wide rename with no functional benefit; treat "status" as meaning
  // "validation status" by convention/documentation, not by name).
  status: MetricStatus;
  limitationText?: string;
  // Below this, a value exists but is unreliable enough that the
  // comparability gate should treat it as unusable for this pair.
  minCoveragePercent?: number;
  accessor: (result: AnalysisResult) => ExtractedMetric | null;
  format: (metric: ExtractedMetric) => string;
  // Decimal places implied by `format` today - declarative metadata for a
  // future generic renderer, not itself used to render (format already
  // does that, and is left untouched - proven, tested code).
  precision?: number;
  // Human-readable pointer to the backend module/function that produces
  // this field - e.g. "quality/scoring.py::build_quality_result". Purely
  // documentation/traceability, matching the spirit of the provenance
  // audit this registry grew out of.
  backendSource: string;
  // The exact analysis_result JSON path this metric's accessor reads -
  // documentation only; the accessor itself remains the executable source
  // of truth, this field just makes the path greppable/testable.
  analysisResultPath: string;
  // = minCoveragePercent !== undefined - whether a per-value coverage/
  // confidence figure gates this metric's inclusion in a trend/comparison.
  confidenceAware: boolean;
  // = category === "biomechanics" today - whether this metric can only
  // exist when a segment's biomechanics were not skipped. Kept explicit
  // (not just inferred from category at every call site) since a future
  // biomechanics-category metric computed pre-gate might not require it.
  requiresBiomechanicsReady: boolean;
  // Mirrors status === "experimental" - sugar for JSX/filter readability
  // (`metric.experimental` reads better inline than a string comparison),
  // always derived together with status so the two can never disagree
  // (see defineMetric below).
  experimental: boolean;
  // A metric with full metadata that isn't surfaced in any UI yet - the
  // mechanism for adding a field to the registry (inventory, future
  // extensibility) without changing any current screen. Every consumer
  // must skip hidden metrics; promoting one later is a one-line flip, not
  // a component rewrite (docs/ENGINEERING_HANDOFF.md §33).
  hidden: boolean;
  comparisonMode: ComparisonMode;
  trendMode: TrendMode;
  // Documents EXISTING behavior only - which value the accessor actually
  // picks when more than one is available. "FIRST_SEGMENT": the first
  // biomechanics-completed segment in the stream (see
  // firstCompletedSegment below - unchanged behavior, just named).
  // "SESSION_LEVEL": one value per whole session, no aggregation needed.
  aggregationMethod: "FIRST_SEGMENT" | "SESSION_LEVEL";
  // Whether an objective winner/ranking can ever be declared for this
  // metric - derived by default from comparisonMode + status (see
  // supportsObjectiveComparison below), individually overridable.
  supportsRanking: boolean;
  // Whether this metric may appear anywhere in the Digital Twin (Progress
  // trend charts, Strengths/Development Areas, Personal Bests). Defaults
  // true; the 10 not-yet-surfaced fields below explicitly set this false
  // so adding their metadata doesn't silently flood the Twin.
  supportsTwin: boolean;
  // Whether this metric may appear in the Coach Console's side-by-side
  // comparison view. Same default/override pattern as supportsTwin.
  supportsCoachComparison: boolean;
  // Forward-looking flags for features that do not exist yet (no
  // Performance Index / AI Potential Score / Talent Score has been built -
  // building one is explicitly out of scope for this registry). Hardcoded
  // false on every metric today; a future feature would filter
  // `METRIC_REGISTRY.filter(m => m.supportsPerformanceIndex)` rather than
  // hardcoding metric keys, once such a feature actually exists.
  supportsPerformanceIndex: boolean;
  supportsFutureScoring: boolean;
  // Pointer to the relevant docs/ENGINEERING_HANDOFF.md section(s), e.g.
  // "§10, §31" for ground-contact-detector reliability.
  documentationReference?: string;
}

// ---------------------------------------------------------------------
// Derivation helpers - the single place trend framing and support-flag
// DEFAULTS are computed from comparisonMode/status. Every default here
// can be overridden per metric (see MetricInput/defineMetric below) - these
// functions exist so the common case takes zero extra authoring, not to
// force every metric into the same answer.
// ---------------------------------------------------------------------

export function deriveDefaultTrendMode(comparisonMode: ComparisonMode): TrendMode {
  switch (comparisonMode) {
    case "HIGHER_IS_BETTER":
      return "INCREASING";
    case "LOWER_IS_BETTER":
      return "DECREASING";
    case "SYMMETRY":
    case "TARGET_RANGE":
      return "MAINTAIN";
    case "NEUTRAL":
      return "NEUTRAL";
    case "EXPERIMENTAL":
      return "EXPERIMENTAL";
    case "NOT_COMPARABLE":
      return "UNKNOWN";
  }
}

// Whether this comparisonMode supports declaring an objective "better"
// value between two sessions/athletes at all - the one definition shared
// by personal-best eligibility, coach-comparison winner-highlighting, and
// Twin strength/development-area generation (previously three separate,
// driftable checks - see docs/ENGINEERING_HANDOFF.md §33).
export function supportsObjectiveComparison(comparisonMode: ComparisonMode): boolean {
  return (
    comparisonMode === "HIGHER_IS_BETTER" ||
    comparisonMode === "LOWER_IS_BETTER" ||
    comparisonMode === "SYMMETRY"
  );
}

function deriveDefaultSupportFlags(
  comparisonMode: ComparisonMode,
  status: MetricStatus,
): { supportsRanking: boolean; supportsTwin: boolean; supportsCoachComparison: boolean } {
  return {
    supportsRanking: supportsObjectiveComparison(comparisonMode) && status === "production",
    supportsTwin: true,
    supportsCoachComparison: true,
  };
}

// Registry-wide invariant violations - returned as data, never thrown.
// Checked by metricRegistry.test.ts (mandatory) - NOT called automatically
// anywhere in this module, so importing metricRegistry.ts can never crash
// the app in production merely because a future entry is malformed
// (docs/ENGINEERING_HANDOFF.md §33).
export interface MetricRegistryViolation {
  key: string;
  message: string;
}

export function validateMetricRegistry(registry: MetricDefinition[]): MetricRegistryViolation[] {
  const violations: MetricRegistryViolation[] = [];
  const seenKeys = new Set<string>();

  for (const metric of registry) {
    if (seenKeys.has(metric.key)) {
      violations.push({ key: metric.key, message: `Duplicate metric key "${metric.key}".` });
    }
    seenKeys.add(metric.key);

    if (metric.status === "experimental" && metric.comparisonMode !== "EXPERIMENTAL") {
      violations.push({
        key: metric.key,
        message: `status "experimental" must have comparisonMode "EXPERIMENTAL", got "${metric.comparisonMode}" - an unreliable detector makes comparison meaningless regardless of raw direction.`,
      });
    }
  }

  return violations;
}

// The authored shape every metric entry actually writes - everything
// mechanically derivable (confidenceAware, requiresBiomechanicsReady,
// experimental, the performanceIndex/futureScoring placeholders) is
// computed once here, in defineMetric, rather than repeated by hand at
// each of the 26 entries below. trendMode/supportsRanking/supportsTwin/
// supportsCoachComparison all get a sensible derived default but may be
// overridden per-entry via `input.field ?? derivedDefault`.
type MetricInput = Pick<
  MetricDefinition,
  | "key"
  | "label"
  | "description"
  | "unit"
  | "category"
  | "subcategory"
  | "applicableEvents"
  | "status"
  | "limitationText"
  | "minCoveragePercent"
  | "accessor"
  | "format"
  | "precision"
  | "backendSource"
  | "analysisResultPath"
  | "comparisonMode"
  | "aggregationMethod"
  | "documentationReference"
> & {
  hidden?: boolean;
  trendMode?: TrendMode;
  supportsRanking?: boolean;
  supportsTwin?: boolean;
  supportsCoachComparison?: boolean;
};

// Exported solely so metricRegistry.test.ts can exercise the actual
// override mechanism directly (trendMode/supportsRanking/supportsTwin/
// supportsCoachComparison) - every current registry entry relies on the
// derived defaults, so testing "override support works" against
// METRIC_REGISTRY alone can't reach that code path.
export function defineMetric(input: MetricInput): MetricDefinition {
  const defaults = deriveDefaultSupportFlags(input.comparisonMode, input.status);

  return {
    ...input,
    hidden: input.hidden ?? false,
    confidenceAware: input.minCoveragePercent !== undefined,
    requiresBiomechanicsReady: input.category === "biomechanics",
    experimental: input.status === "experimental",
    trendMode: input.trendMode ?? deriveDefaultTrendMode(input.comparisonMode),
    supportsRanking: input.supportsRanking ?? defaults.supportsRanking,
    supportsTwin: input.supportsTwin ?? defaults.supportsTwin,
    supportsCoachComparison: input.supportsCoachComparison ?? defaults.supportsCoachComparison,
    supportsPerformanceIndex: false,
    supportsFutureScoring: false,
  };
}

function firstCompletedSegment(result: AnalysisResult): any | null {
  if (!result) return null;
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
// comparisonMode is NEUTRAL for all six: a joint angle has an ideal range
// dependent on many factors, not a bigger-or-smaller-is-better direction
// (docs/ENGINEERING_HANDOFF.md §33 - this was, until this pass, silently
// treated as HIGHER_IS_BETTER by every Twin/comparison consumer).
const JOINT_ANGLE_DEFINITIONS: { key: string; label: string }[] = [
  { key: "left_knee", label: "Left Knee Angle" },
  { key: "right_knee", label: "Right Knee Angle" },
  { key: "left_hip", label: "Left Hip Angle" },
  { key: "right_hip", label: "Right Hip Angle" },
  { key: "left_elbow", label: "Left Elbow Angle" },
  { key: "right_elbow", label: "Right Elbow Angle" },
];

function buildJointAngleMetrics(): MetricDefinition[] {
  return JOINT_ANGLE_DEFINITIONS.map(({ key, label }) =>
    defineMetric({
      key: `joint_angle_${key}`,
      label,
      description: `Mean ${label.toLowerCase()} across the analysed segment.`,
      unit: "deg",
      category: "biomechanics",
      subcategory: "joint_angle",
      applicableEvents: ["Sprint"],
      status: "production",
      minCoveragePercent: 60,
      comparisonMode: "NEUTRAL",
      aggregationMethod: "FIRST_SEGMENT",
      backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (joint_angles)",
      analysisResultPath: `biomechanics.segments[].joint_angles.${key}.mean_degrees`,
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
    }),
  );
}

// Ten additional live, real fields (docs/ENGINEERING_HANDOFF.md §33's
// metric-registry inventory pass) that are already computed by the live
// quality gate but, until now, were only ever displayed via
// PerformanceDetail.tsx's bespoke, single-report gate tables - never
// registry-governed, never comparable/trendable. Added here with full
// metadata (satisfying the inventory + future-extensibility requirement)
// but marked `hidden: true` / `supportsTwin: false` /
// `supportsCoachComparison: false` deliberately: this pass's job is fixing
// comparison SEMANTICS for metrics already exposed, not adding new
// comparison surfaces to the Athlete Console or Coach Console. Promoting
// any of these later is a one-line flip (remove `hidden`/the two
// `supports*` overrides), not a component rewrite.
function buildVisibilityMetrics(): MetricDefinition[] {
  const groups: { key: string; label: string }[] = [
    { key: "hips", label: "Hips Visibility" },
    { key: "knees", label: "Knees Visibility" },
    { key: "ankles", label: "Ankles Visibility" },
    { key: "feet", label: "Feet Visibility" },
  ];
  return groups.map(({ key, label }) =>
    defineMetric({
      key: `visibility_${key}`,
      label,
      description: `Percentage of analysed frames in which the athlete's ${key} were visible to the camera.`,
      unit: "%",
      category: "recording_quality",
      subcategory: "joint_visibility",
      applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
      status: "production",
      comparisonMode: "HIGHER_IS_BETTER",
      aggregationMethod: "SESSION_LEVEL",
      backendSource: "quality/scoring.py::build_quality_result (body_visibility)",
      analysisResultPath: `recording_quality.body_visibility.${key}`,
      hidden: true,
      supportsTwin: false,
      supportsCoachComparison: false,
      accessor: (result) => {
        const quality = result.recording_quality as any;
        const value = quality?.body_visibility?.[key];
        return typeof value === "number" ? { value } : null;
      },
      format: (m) => `${Math.round(m.value)}%`,
    }),
  );
}

function buildQualitySubScoreMetrics(): MetricDefinition[] {
  const scores: { path: string; label: string }[] = [
    { path: "camera_angle_score", label: "Camera Angle Score" },
    { path: "camera_height_score", label: "Camera Height Score" },
    { path: "lighting_score", label: "Lighting Score" },
    { path: "sharpness_score", label: "Sharpness Score" },
    { path: "frame_rate_score", label: "Frame Rate Score" },
  ];
  return scores.map(({ path, label }) =>
    defineMetric({
      key: path,
      label,
      description: `${label} from the recording-quality gate - informational; does not itself gate biomechanics_ready.`,
      unit: "/100",
      category: "recording_quality",
      subcategory: "quality_subscore",
      applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
      status: "production",
      comparisonMode: "HIGHER_IS_BETTER",
      aggregationMethod: "SESSION_LEVEL",
      backendSource: "quality/scoring.py::build_quality_result (metrics)",
      analysisResultPath: `recording_quality.metrics.${path}`,
      hidden: true,
      supportsTwin: false,
      supportsCoachComparison: false,
      accessor: (result) => {
        const quality = result.recording_quality as any;
        const value = quality?.metrics?.[path];
        return typeof value === "number" ? { value } : null;
      },
      format: (m) => `${Math.round(m.value)}/100`,
    }),
  );
}

export const METRIC_REGISTRY: MetricDefinition[] = [
  defineMetric({
    key: "detection_rate",
    label: "Detection Rate",
    description: "Percentage of analysed frames in which a pose was detected at all.",
    unit: "%",
    category: "recording_quality",
    subcategory: "tracking",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "SESSION_LEVEL",
    backendSource: "pose_remote/live_analyzer.py (analysis.detection_rate_percent)",
    analysisResultPath: "analysis.detection_rate_percent",
    accessor: (result) => {
      const value = result.analysis?.detection_rate_percent;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}%`,
  }),
  defineMetric({
    key: "readiness_score",
    label: "Recording Readiness Score",
    description: "Composite score of whether the recording was captured well enough to analyze.",
    unit: "/100",
    category: "recording_quality",
    subcategory: "readiness",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    limitationText:
      "Reflects whether the recording was captured well enough to analyze - not an athletic performance score. Do not read a higher number here as \"a better athlete.\"",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "SESSION_LEVEL",
    backendSource: "quality/scoring.py::build_quality_result (analysis_readiness.score)",
    analysisResultPath: "recording_quality.analysis_readiness.score",
    documentationReference: "§6, §7",
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.analysis_readiness?.score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}/100`,
  }),
  // Cadence and stride frequency: comparisonMode is HIGHER_IS_BETTER,
  // restored to match existing, already-shipped, test-locked product
  // behavior (docs/ENGINEERING_HANDOFF.md §33 - re-evaluated a second
  // time on explicit review, after the first pass's reclassification to
  // NEUTRAL broke 8 pre-existing twinEngine.test.ts assertions that the
  // live Digital Twin already treats cadence as rankable - eligible for
  // Personal Bests, Strengths, and Evolution Statements). This migration
  // centralizes existing semantics; it does not redefine product
  // behavior. HIGHER_IS_BETTER here is a product-interpretation decision,
  // not a sports-science claim - see limitationText, which says so
  // explicitly rather than silently implying a universally validated
  // coaching rule.
  defineMetric({
    key: "cadence",
    label: "Cadence",
    description: "Estimated steps per minute over the analysed segment.",
    unit: "steps/min",
    category: "biomechanics",
    subcategory: "gait_timing",
    applicableEvents: ["Sprint"],
    status: "production",
    limitationText:
      "This platform currently interprets a higher cadence positively for longitudinal Digital Twin comparisons. Optimal cadence depends on the individual athlete, sprint phase, event, and running speed - this interpretation should not be treated as a universally validated coaching rule.",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "FIRST_SEGMENT",
    backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (cadence)",
    analysisResultPath: "biomechanics.segments[].cadence.steps_per_minute",
    documentationReference: "§33",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.cadence?.steps_per_minute;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)} steps/min`,
  }),
  defineMetric({
    key: "stride_frequency",
    label: "Stride Frequency",
    description: "Estimated stride frequency across the analysed segment.",
    unit: "Hz",
    category: "biomechanics",
    subcategory: "gait_timing",
    applicableEvents: ["Sprint"],
    status: "production",
    limitationText:
      "This platform currently interprets a higher stride frequency positively for longitudinal Digital Twin comparisons. Optimal stride frequency depends on the individual athlete, sprint phase, event, and running speed - this interpretation should not be treated as a universally validated coaching rule.",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "FIRST_SEGMENT",
    backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (stride)",
    analysisResultPath: "biomechanics.segments[].stride.stride_frequency_hz",
    documentationReference: "§33",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.stride?.stride_frequency_hz;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${m.value.toFixed(2)} Hz`,
  }),
  defineMetric({
    key: "knee_symmetry",
    label: "Knee Symmetry",
    description: "Left/right knee-angle symmetry score - already encodes 'closer to symmetric' as a higher score.",
    unit: "%",
    category: "biomechanics",
    subcategory: "symmetry",
    applicableEvents: ["Sprint"],
    status: "production",
    comparisonMode: "SYMMETRY",
    aggregationMethod: "FIRST_SEGMENT",
    backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (knee_symmetry_score)",
    analysisResultPath: "biomechanics.segments[].knee_symmetry_score",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.knee_symmetry_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}%`,
  }),
  defineMetric({
    key: "body_visibility",
    label: "Body Visibility",
    description:
      "Whether the camera captured the athlete's full body well - a recording-quality signal, never an athletic-performance one. A rising trend means recordings got more consistent, not that the athlete improved.",
    unit: "%",
    // Categorized recording_quality, not biomechanics, deliberately -
    // this measures whether the CAMERA captured the athlete's full body
    // well, not what the athlete's body is doing. The Digital Twin must
    // never present a rising trend here as "the athlete improved" (see
    // docs/ENGINEERING_HANDOFF.md, Digital Twin architecture proposal).
    category: "recording_quality",
    subcategory: "visibility",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "SESSION_LEVEL",
    backendSource: "quality/scoring.py::build_quality_result (metrics.full_body_visibility_score)",
    analysisResultPath: "recording_quality.metrics.full_body_visibility_score",
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.metrics?.full_body_visibility_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}%`,
  }),
  defineMetric({
    key: "movement_quality",
    label: "Movement Quality",
    description:
      "How much genuine athletic motion was detected on camera (used to reject a standing-pose recording) - recording-quality signal, not a judgment of athletic ability.",
    unit: "/100",
    // Same reasoning as body_visibility above - this is the quality
    // gate's athlete_movement_score (how much genuine athletic motion
    // was detected on camera, used to reject a standing-pose recording),
    // not a judgment of athletic ability. recording_quality category.
    category: "recording_quality",
    subcategory: "movement",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "SESSION_LEVEL",
    backendSource: "quality/scoring.py::build_quality_result (metrics.athlete_movement_score)",
    analysisResultPath: "recording_quality.metrics.athlete_movement_score",
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.metrics?.athlete_movement_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}/100`,
  }),
  defineMetric({
    key: "ground_contacts",
    label: "Ground Contacts",
    description: "Count of detected ground-contact events in the analysed segment.",
    unit: "detected",
    category: "biomechanics",
    subcategory: "gait_timing",
    applicableEvents: ["Sprint"],
    status: "experimental",
    limitationText:
      "Ground-contact detection is confirmed unreliable for some camera angles - a hand-labeled counterexample showed a true contact scoring lower on the only signal this detector uses than a confirmed false positive. Not a trustworthy selection criterion yet.",
    comparisonMode: "EXPERIMENTAL",
    aggregationMethod: "FIRST_SEGMENT",
    backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (ground_contact.events)",
    analysisResultPath: "biomechanics.segments[].ground_contact.events",
    documentationReference: "§10, §11",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.ground_contact?.events;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)} detected`,
  }),
  defineMetric({
    key: "duty_factor",
    label: "Duty Factor",
    description: "Percentage of the stride cycle spent in ground contact - derived from ground-contact detection.",
    unit: "%",
    category: "biomechanics",
    subcategory: "gait_timing",
    applicableEvents: ["Sprint"],
    status: "experimental",
    limitationText: "Derived from ground-contact detection - inherits the same unreliability.",
    comparisonMode: "EXPERIMENTAL",
    aggregationMethod: "FIRST_SEGMENT",
    backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (duty_factor_percent)",
    analysisResultPath: "biomechanics.segments[].duty_factor_percent",
    documentationReference: "§10, §11",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.duty_factor_percent;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${m.value.toFixed(1)}%`,
  }),
  defineMetric({
    key: "flight_time",
    label: "Flight Time",
    description: "Median airborne time between ground contacts - derived from ground-contact detection.",
    unit: "ms",
    category: "biomechanics",
    subcategory: "gait_timing",
    applicableEvents: ["Sprint"],
    status: "experimental",
    limitationText: "Derived from ground-contact detection - inherits the same unreliability.",
    comparisonMode: "EXPERIMENTAL",
    aggregationMethod: "FIRST_SEGMENT",
    backendSource: "reports/sprint_segment_report.py::build_sprint_segment_report (flight_time)",
    analysisResultPath: "biomechanics.segments[].flight_time.median_flight_time_ms",
    documentationReference: "§10, §11",
    accessor: (result) => {
      const segment = firstCompletedSegment(result);
      const value = segment?.flight_time?.median_flight_time_ms;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)} ms`,
  }),
  ...buildJointAngleMetrics(),
  defineMetric({
    key: "tracking_confidence",
    label: "Tracking Confidence",
    description:
      "Pose-detection confidence score from the quality gate. Live and real, but not yet registry-governed anywhere beyond PerformanceDetail's diagnostic gate table - see docs/ENGINEERING_HANDOFF.md §33.",
    unit: "/100",
    category: "recording_quality",
    subcategory: "tracking",
    applicableEvents: ["Sprint", "Hurdles", "Long Jump", "High Jump"],
    status: "production",
    comparisonMode: "HIGHER_IS_BETTER",
    aggregationMethod: "SESSION_LEVEL",
    backendSource: "quality/scoring.py::build_quality_result (metrics.pose_detection_score)",
    analysisResultPath: "recording_quality.metrics.pose_detection_score",
    hidden: true,
    supportsTwin: false,
    supportsCoachComparison: false,
    accessor: (result) => {
      const quality = result.recording_quality as any;
      const value = quality?.metrics?.pose_detection_score;
      return typeof value === "number" ? { value } : null;
    },
    format: (m) => `${Math.round(m.value)}/100`,
  }),
  ...buildVisibilityMetrics(),
  ...buildQualitySubScoreMetrics(),
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
