import {
  AlertTriangle,
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock3,
  FileVideo,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ROUTES } from "../../../constants/routes";
import { usePerformance } from "../hooks/usePerformance";
import { useRetryAnalysis } from "../hooks/useRetryAnalysis";
import { useAnalysisPolling } from "../hooks/useAnalysisPolling";
import type { AnalysisResult } from "../types/analysis";

// Postgres's jsonb column type does not preserve object key insertion
// order - it re-serializes keys sorted by (length, then alphabetically),
// so analysis_result's joint_angles keys come back scrambled on every
// read regardless of what order the backend produced. Sort explicitly by
// this canonical order instead of trusting Object.entries() order.
const JOINT_ANGLE_ORDER = [
  "left_knee",
  "right_knee",
  "left_hip",
  "right_hip",
  "left_elbow",
  "right_elbow",
];

function sortJointAngleEntries(jointAngles: Record<string, any>) {
  return Object.entries(jointAngles).sort(([a], [b]) => {
    const indexA = JOINT_ANGLE_ORDER.indexOf(a);
    const indexB = JOINT_ANGLE_ORDER.indexOf(b);
    if (indexA === -1 && indexB === -1) return a.localeCompare(b);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
  });
}

function getEventName(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as
      | { name?: string; category?: string }
      | undefined;

    return firstEvent?.name ?? "Performance";
  }

  if (events && typeof events === "object" && "name" in events) {
    return (events as { name?: string }).name ?? "Performance";
  }

  return "Performance";
}

function getEventCategory(events: unknown) {
  if (Array.isArray(events)) {
    const firstEvent = events[0] as
      | { name?: string; category?: string }
      | undefined;

    return firstEvent?.category ?? "Athletics";
  }

  if (events && typeof events === "object" && "category" in events) {
    return (events as { category?: string }).category ?? "Athletics";
  }

  return "Athletics";
}

function getStatusLabel(status: string | null) {
  switch (status) {
    case "completed":
      return "Completed";
    case "processing":
      return "Processing";
    case "analyzing":
      return "Analyzing";
    case "failed":
      return "Failed";
    default:
      return "Uploaded";
  }
}

function getStatusClasses(status: string | null) {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-700";
    case "processing":
    case "analyzing":
      return "bg-blue-100 text-blue-700";
    case "failed":
      return "bg-red-100 text-red-700";
    default:
      return "bg-orange-100 text-[#F0600E]";
  }
}

function formatDate(date?: string | null) {
  if (!date) return "Date unavailable";

  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(date));
}

function StatTile({
  label,
  value,
  caveat,
}: {
  label: string;
  value: string;
  caveat?: string;
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4">
      <p className="text-xs font-bold uppercase tracking-widest text-gray-400">
        {label}
      </p>
      <p className="mt-1 text-lg font-bold text-gray-950">{value}</p>
      {caveat && <p className="mt-1 text-xs text-amber-600">{caveat}</p>}
    </div>
  );
}

function SegmentReport({ segment, index }: { segment: any; index: number }) {
  if (segment?.status !== "completed") {
    return (
      <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
        <p className="text-sm font-bold text-gray-950">
          Segment {index + 1}
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Biomechanics not available for this segment
          {segment?.reason ? `: ${segment.reason}` : "."}
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-3xl border border-gray-200 bg-white p-5">
      <p className="text-sm font-bold text-gray-950">Segment {index + 1}</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label="Cadence"
          value={
            segment.cadence?.steps_per_minute
              ? `${Math.round(segment.cadence.steps_per_minute)} steps/min`
              : "N/A"
          }
        />
        <StatTile
          label="Stride Frequency"
          value={
            segment.stride?.stride_frequency_hz
              ? `${segment.stride.stride_frequency_hz.toFixed(2)} Hz`
              : "N/A"
          }
        />
        <StatTile
          label="Ground Contacts"
          value={
            segment.ground_contact?.events !== undefined
              ? `${segment.ground_contact.events} detected`
              : "N/A"
          }
          caveat="Experimental - not yet validated for all camera angles"
        />
        <StatTile
          label="Duty Factor"
          value={
            segment.duty_factor_percent !== undefined &&
            segment.duty_factor_percent !== null
              ? `${segment.duty_factor_percent.toFixed(1)}%`
              : "N/A"
          }
          caveat="Experimental - not yet validated for all camera angles"
        />
        <StatTile
          label="Flight Time"
          value={
            segment.flight_time?.median_flight_time_ms
              ? `${Math.round(segment.flight_time.median_flight_time_ms)} ms`
              : "N/A"
          }
        />
        <StatTile
          label="Knee Symmetry"
          value={
            segment.knee_symmetry_score !== undefined &&
            segment.knee_symmetry_score !== null
              ? `${Math.round(segment.knee_symmetry_score)}%`
              : "N/A"
          }
        />
      </div>

      {segment.joint_angles && Object.keys(segment.joint_angles).length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[480px] text-left text-sm">
            <thead>
              <tr className="text-xs font-bold uppercase tracking-widest text-gray-400">
                <th className="pb-2">Joint</th>
                <th className="pb-2">Mean</th>
                <th className="pb-2">Min</th>
                <th className="pb-2">Max</th>
                <th className="pb-2">Coverage</th>
              </tr>
            </thead>
            <tbody>
              {sortJointAngleEntries(segment.joint_angles).map(([key, joint]: [string, any]) => (
                <tr key={key} className="border-t border-gray-100">
                  <td className="py-2 font-semibold text-gray-800">
                    {joint.label}
                  </td>
                  <td className="py-2 text-gray-600">
                    {joint.mean_degrees !== null && joint.mean_degrees !== undefined
                      ? `${joint.mean_degrees.toFixed(0)}°`
                      : "—"}
                  </td>
                  <td className="py-2 text-gray-600">
                    {joint.min_degrees !== null && joint.min_degrees !== undefined
                      ? `${joint.min_degrees.toFixed(0)}°`
                      : "—"}
                  </td>
                  <td className="py-2 text-gray-600">
                    {joint.max_degrees !== null && joint.max_degrees !== undefined
                      ? `${joint.max_degrees.toFixed(0)}°`
                      : "—"}
                  </td>
                  <td className="py-2 text-gray-600">
                    {joint.coverage_percent !== null && joint.coverage_percent !== undefined
                      ? `${joint.coverage_percent.toFixed(0)}%`
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}

type CheckRow = {
  label: string;
  passed: boolean;
  value: string;
  required?: string;
};

// All of this reads fields the backend already sends in recording_quality
// - nothing here changes what passes or fails, it only explains the same
// gate result more specifically than the backend's single rating string.
// Priority mirrors biomechanics_ready's actual condition order in
// backend/app/services/quality/scoring.py (camera angle first - nothing
// else is meaningful if the angle is wrong - then the worst individual
// body-part visibility, then the composite, then camera height, then
// movement, then a generic fallback).
export function diagnoseSkipReason(quality: any): string {
  const view = quality?.camera_view?.classification;
  const bodyVisibility = quality?.body_visibility ?? {};
  const metrics = quality?.metrics ?? {};

  if (view === "Front View") {
    return "the camera is recording from the front rather than the side. Reposition to a true side-on view of the athlete.";
  }

  if (view === "Three-Quarter View") {
    return "the camera angle is three-quarter rather than a true side view. Move directly to the athlete's side.";
  }

  if (!view || view === "Unknown") {
    return "the camera angle could not be reliably determined from this recording.";
  }

  const bodyParts: Array<{ label: string; value: number | undefined }> = [
    { label: "feet", value: bodyVisibility.feet },
    { label: "ankles", value: bodyVisibility.ankles },
    { label: "knees", value: bodyVisibility.knees },
    { label: "hips", value: bodyVisibility.hips },
  ];

  const failingParts = bodyParts
    .filter(
      (part): part is { label: string; value: number } =>
        typeof part.value === "number" && part.value < 70,
    )
    .sort((a, b) => a.value - b.value);

  if (failingParts.length > 0) {
    const worst = failingParts[0];
    return (
      `the athlete's ${worst.label} were visible in only ` +
      `${Math.round(worst.value)}% of analysed frames (at least 70% is ` +
      `required). Keep the full body, including ${worst.label}, inside ` +
      `the frame throughout the run.`
    );
  }

  if (
    typeof metrics.full_body_visibility_score === "number" &&
    metrics.full_body_visibility_score < 75
  ) {
    return (
      `the athlete's full body was only visible in ` +
      `${Math.round(metrics.full_body_visibility_score)}% of frames on ` +
      `average (at least 75% is required).`
    );
  }

  if (
    typeof metrics.camera_height_score === "number" &&
    metrics.camera_height_score < 60
  ) {
    return "the camera appears to be positioned too low or tilted upward, leaving too much empty space above the athlete. Raise the camera to roughly waist height and keep the shot level.";
  }

  if (
    typeof metrics.athlete_movement_score === "number" &&
    metrics.athlete_movement_score < 50
  ) {
    return "not enough athletic movement was detected in this recording - this looks like a standing pose rather than an actual run.";
  }

  return quality?.analysis_readiness?.rating
    ? `the recording did not meet the requirements for biomechanics analysis (${quality.analysis_readiness.rating}).`
    : "the recording did not meet the requirements for biomechanics analysis.";
}

// The hard checks that actually gate biomechanics_ready, in the same
// order as the boolean formula in scoring.py.
export function buildGatingChecks(quality: any): CheckRow[] {
  const view = quality?.camera_view?.classification;
  const bodyVisibility = quality?.body_visibility ?? {};
  const metrics = quality?.metrics ?? {};
  const readiness = quality?.analysis_readiness ?? {};

  const checks: CheckRow[] = [
    {
      label: "Camera angle",
      passed: view === "Side View",
      value: view ?? "Unknown",
      required: "Side View",
    },
  ];

  const bodyGroups: Array<[string, string]> = [
    ["hips", "Hips visibility"],
    ["knees", "Knees visibility"],
    ["ankles", "Ankles visibility"],
    ["feet", "Feet visibility"],
  ];

  for (const [key, label] of bodyGroups) {
    const value = bodyVisibility[key];
    if (typeof value === "number") {
      checks.push({
        label,
        passed: value >= 70,
        value: `${Math.round(value)}%`,
        required: "≥ 70%",
      });
    }
  }

  if (typeof metrics.full_body_visibility_score === "number") {
    checks.push({
      label: "Overall body visibility",
      passed: metrics.full_body_visibility_score >= 75,
      value: `${Math.round(metrics.full_body_visibility_score)}%`,
      required: "≥ 75%",
    });
  }

  if (typeof metrics.athlete_movement_score === "number") {
    checks.push({
      label: "Athlete movement",
      passed: metrics.athlete_movement_score >= 50,
      value: `${Math.round(metrics.athlete_movement_score)}/100`,
      required: "≥ 50/100",
    });
  }

  if (typeof metrics.camera_height_score === "number") {
    checks.push({
      label: "Camera height",
      passed: metrics.camera_height_score >= 60,
      value: `${Math.round(metrics.camera_height_score)}/100`,
      required: "≥ 60/100",
    });
  }

  if (typeof readiness.score === "number") {
    checks.push({
      label: "Overall readiness score",
      passed: readiness.score >= 70,
      value: `${Math.round(readiness.score)}/100`,
      required: "≥ 70/100",
    });
  }

  return checks;
}

// Informational only - none of these gate biomechanics_ready on their
// own (see scoring.py), so they get no "required" column value.
export function buildQualityChecks(quality: any): CheckRow[] {
  const metrics = quality?.metrics ?? {};
  const informational: Array<[string, string]> = [
    ["lighting_score", "Lighting"],
    ["sharpness_score", "Sharpness"],
    ["frame_rate_score", "Frame rate"],
    ["pose_detection_score", "Pose tracking confidence"],
    ["athlete_occupancy_score", "Framing distance"],
  ];

  return informational
    .filter(([key]) => typeof metrics[key] === "number")
    .map(([key, label]) => ({
      label,
      passed: metrics[key] >= 70,
      value: `${Math.round(metrics[key])}/100`,
    }));
}

function CheckTable({ title, checks }: { title: string; checks: CheckRow[] }) {
  if (checks.length === 0) return null;

  return (
    <div className="mt-4">
      <p className="text-xs font-bold uppercase tracking-widest text-gray-400">
        {title}
      </p>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[420px] text-left text-sm">
          <thead>
            <tr className="text-xs font-bold uppercase tracking-widest text-gray-400">
              <th className="pb-2">Check</th>
              <th className="pb-2">Value</th>
              <th className="pb-2">Required</th>
              <th className="pb-2">Result</th>
            </tr>
          </thead>
          <tbody>
            {checks.map((check) => (
              <tr key={check.label} className="border-t border-gray-100">
                <td className="py-2 font-semibold text-gray-800">
                  {check.label}
                </td>
                <td className="py-2 text-gray-600">{check.value}</td>
                <td className="py-2 text-gray-500">{check.required ?? "—"}</td>
                <td className="py-2">
                  <span
                    className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-bold ${
                      check.passed
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {check.passed ? "Passed" : "Failed"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function QualityGateBreakdown({ quality }: { quality: any }) {
  const gatingChecks = buildGatingChecks(quality);
  const qualityChecks = buildQualityChecks(quality);
  const diagnosis = diagnoseSkipReason(quality);

  return (
    <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
      <p className="text-sm leading-6 text-gray-700">
        Biomechanics analysis could not be completed because {diagnosis}
      </p>

      <CheckTable title="Biomechanics Readiness Checks" checks={gatingChecks} />
      <CheckTable title="General Recording Quality" checks={qualityChecks} />
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-gray-400">
      {children}
    </p>
  );
}

export function AnalysisReport({ result }: { result: AnalysisResult }) {
  const quality = result.recording_quality as any;
  const biomechanics = result.biomechanics as any;
  const warnings: string[] = Array.isArray(quality?.warnings)
    ? quality.warnings
    : [];
  const recommendations: string[] = Array.isArray(quality?.recommendations)
    ? quality.recommendations
    : [];

  const segments: any[] = Array.isArray(biomechanics?.segments) ? biomechanics.segments : [];
  const segmentLimitations = Array.from(
    new Set(
      segments.flatMap((segment) =>
        Array.isArray(segment?.limitations) ? segment.limitations : [],
      ),
    ),
  );
  const limitations: string[] =
    biomechanics?.status === "skipped"
      ? ["Biomechanics analysis was skipped for this recording - see the readiness checks above for why."]
      : segmentLimitations;

  return (
    <div className="space-y-4">
      <div>
        <SectionHeading>AI Analysis</SectionHeading>
        <div className="grid gap-4 sm:grid-cols-2">
          <StatTile
            label="Detection Rate"
            value={`${result.analysis?.detection_rate_percent?.toFixed(0) ?? "N/A"}%`}
          />
          <StatTile
            label="Duration"
            value={`${result.video?.duration_seconds?.toFixed(1) ?? "N/A"}s`}
          />
        </div>
      </div>

      <div>
        <SectionHeading>Recording Quality</SectionHeading>
        <div className="grid gap-4 sm:grid-cols-2">
          <StatTile
            label="Recording Quality"
            value={quality?.rating ?? "N/A"}
          />
          <StatTile
            label="Camera View"
            value={quality?.camera_view?.classification ?? "N/A"}
          />
        </div>

        {warnings.length > 0 && (
          <div className="mt-4 rounded-3xl border border-amber-200 bg-amber-50 p-5">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-700" />
              <p className="text-sm font-bold text-amber-900">
                Recording Quality Notes
              </p>
            </div>

            <ul className="mt-3 space-y-1 text-sm text-amber-800">
              {warnings.map((note) => (
                <li key={note}>• {note}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div>
        <SectionHeading>Biomechanics</SectionHeading>

        {biomechanics?.status === "skipped" ? (
          <QualityGateBreakdown quality={quality} />
        ) : segments.length > 0 ? (
          <div className="space-y-4">
            {segments.map((segment: any, index: number) => (
              <SegmentReport key={index} segment={segment} index={index} />
            ))}
          </div>
        ) : (
          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <p className="text-sm text-gray-600">
              No biomechanics segments were produced for this recording.
            </p>
          </div>
        )}
      </div>

      {limitations.length > 0 && (
        <div>
          <SectionHeading>Limitations</SectionHeading>
          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <ul className="space-y-1.5 text-sm leading-6 text-gray-600">
              {limitations.map((note) => (
                <li key={note}>• {note}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {recommendations.length > 0 && (
        <div>
          <SectionHeading>Recommendations</SectionHeading>
          <div className="rounded-3xl border border-blue-200 bg-blue-50 p-5">
            <ul className="space-y-1.5 text-sm leading-6 text-blue-800">
              {recommendations.map((note) => (
                <li key={note}>• {note}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="rounded-3xl border border-dashed border-gray-300 bg-gray-50 p-5">
        <p className="text-xs font-bold uppercase tracking-widest text-gray-400">
          Coming Soon
        </p>
        <p className="mt-2 text-sm leading-6 text-gray-500">
          Sprint Score and elite-athlete comparison are on the roadmap but not
          built yet - they need real, licensed reference data before they can
          ship responsibly.
        </p>
      </div>
    </div>
  );
}

export default function PerformanceDetail() {
  const { performanceId } = useParams();
  const { data: performance, isLoading, error } =
    usePerformance(performanceId);
  const retryAnalysis = useRetryAnalysis();

  // PerformanceProcessing.tsx polls while it's mounted, but a user who
  // navigates away (e.g. back to the dashboard) before a job finishes
  // stops that polling - nothing else ever checks again, so the row can
  // stay stuck on "analyzing" forever even after the backend genuinely
  // completed the job. Landing on this page for a not-yet-terminal
  // performance is exactly the moment to reconcile: poll once (and keep
  // polling, bounded, while this page stays open) and persist whatever
  // the backend actually says.
  const jobId =
    performance?.analysis_job_id &&
    performance?.upload_status !== "completed" &&
    performance?.upload_status !== "failed"
      ? (performance.analysis_job_id as string)
      : undefined;

  const analysisPoll = useAnalysisPolling(performanceId, jobId);

  function handleRetry() {
    if (!performance || !performance.video_url) return;
    retryAnalysis.retry({
      performanceId: performance.id,
      videoPath: performance.video_url as string,
    });
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-gray-200 bg-white p-10 text-center shadow-sm">
        <Loader2 className="mx-auto h-9 w-9 animate-spin text-[#F0600E]" />

        <p className="mt-4 text-sm font-bold text-gray-600">
          Loading performance...
        </p>
      </div>
    );
  }

  if (error || !performance) {
    return (
      <div className="mx-auto max-w-5xl rounded-4xl border border-red-200 bg-red-50 p-10 text-center">
        <h1 className="text-2xl font-bold text-red-700">
          Unable to load this performance.
        </h1>

        <Link
          to={ROUTES.ATHLETE.HISTORY}
          className="mt-6 inline-flex rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white"
        >
          Return to Performances
        </Link>
      </div>
    );
  }

  const status = performance.upload_status;
  const isProcessing =
    status === "uploaded" ||
    status === "processing" ||
    status === "analyzing";

  return (
    <div className="mx-auto max-w-6xl">
      <Link
        to={ROUTES.ATHLETE.HISTORY}
        className="inline-flex items-center gap-2 text-sm font-bold text-gray-600 transition hover:text-[#F0600E]"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to My Performances
      </Link>

      <div className="mt-6 rounded-4xl border border-gray-200 bg-white p-7 shadow-xl shadow-gray-200/60 md:p-9">
        <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-start">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
                Performance #
                {String(performance.performance_number ?? 0).padStart(2, "0")}
              </p>

              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${getStatusClasses(
                  status,
                )}`}
              >
                {getStatusLabel(status)}
              </span>
            </div>

            <h1 className="mt-4 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
              {performance.title}
            </h1>

            <p className="mt-4 flex flex-wrap items-center gap-2 text-sm text-gray-500">
              <CalendarDays className="h-4 w-4" />
              {formatDate(performance.performance_date)}
              <span aria-hidden="true">·</span>
              {getEventName(performance.events)}
            </p>
          </div>

          {isProcessing && (
            <Link
              to={ROUTES.ATHLETE.PERFORMANCE_PROCESSING(performance.id)}
              className="inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700"
            >
              <Loader2 className="h-4 w-4 animate-spin" />
              View Analysis Status
            </Link>
          )}
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <FileVideo className="h-5 w-5 text-[#F0600E]" />

            <p className="mt-4 text-xs font-bold uppercase tracking-widest text-gray-400">
              Event
            </p>

            <p className="mt-2 text-xl font-bold text-gray-950">
              {getEventName(performance.events)}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              {getEventCategory(performance.events)}
            </p>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <Clock3 className="h-5 w-5 text-[#F0600E]" />

            <p className="mt-4 text-xs font-bold uppercase tracking-widest text-gray-400">
              Current Status
            </p>

            <p className="mt-2 text-xl font-bold text-gray-950">
              {getStatusLabel(status)}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              {isProcessing
                ? "Your performance report is being prepared."
                : "Your performance has been processed."}
            </p>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-gray-50 p-5">
            <CheckCircle2 className="h-5 w-5 text-green-700" />

            <p className="mt-4 text-xs font-bold uppercase tracking-widest text-gray-400">
              AI Report
            </p>

            <p className="mt-2 text-xl font-bold text-gray-950">
              {status === "completed" ? "Ready" : "Pending"}
            </p>

            <p className="mt-1 text-sm text-gray-500">
              Shakti Motion Intelligence™ analysis
            </p>
          </div>
        </div>

        <div className="mt-6 rounded-3xl border border-gray-200 bg-white p-6">
          <p className="font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-gray-400">
            Session Notes
          </p>

          <p className="mt-3 text-sm leading-7 text-gray-600">
            {performance.notes || "No additional notes were added."}
          </p>
        </div>

        {status === "completed" && performance.analysis_result ? (
          <div className="mt-6">
            <p className="mb-4 font-['JetBrains_Mono'] text-xs font-bold uppercase tracking-[0.2em] text-[#F0600E]">
              Shakti Motion Intelligence™ Report
            </p>

            <AnalysisReport
              result={performance.analysis_result as AnalysisResult}
            />
          </div>
        ) : status === "failed" ? (
          <div className="mt-6 rounded-3xl border border-red-200 bg-red-50 p-6">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-700" />
              <p className="text-sm font-bold text-red-900">
                Analysis Failed
              </p>
            </div>

            <p className="mt-2 text-sm leading-6 text-red-700">
              {(performance.analysis_error as string | null) ||
                "Analysis could not be completed for this recording."}
            </p>

            {retryAnalysis.error && (
              <p className="mt-2 text-sm leading-6 text-red-600">
                Retry failed: {retryAnalysis.error.message}
              </p>
            )}

            <button
              type="button"
              onClick={handleRetry}
              disabled={retryAnalysis.isPending}
              className="mt-4 inline-flex items-center gap-2 rounded-xl bg-[#F0600E] px-5 py-3 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={`h-4 w-4 ${retryAnalysis.isPending ? "animate-spin" : ""}`}
              />
              {retryAnalysis.isPending ? "Retrying..." : "Retry Analysis"}
            </button>
          </div>
        ) : (
          <div className="mt-6 rounded-3xl border border-orange-200 bg-[#FFF8F3] p-6">
            <p className="text-sm font-bold text-gray-950">
              Shakti Motion Intelligence™
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-600">
              Biomechanical metrics, movement insights, performance scoring,
              and coaching recommendations will appear here when the
              analysis is completed.
            </p>

            {jobId && (
              <p className="mt-3 flex items-center gap-2 text-xs font-semibold text-gray-500">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                {analysisPoll.timedOut
                  ? "This is taking longer than usual - check back later."
                  : "Checking analysis status..."}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}