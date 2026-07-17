// Canonical "extract the useful summary fields from one analysis_result"
// function - used by the Digital Twin and by AthleteReports.tsx, which
// previously had its own independent, ad-hoc version of this same
// extraction (extractReportSummary, consolidated onto this function - see
// docs/ENGINEERING_HANDOFF.md).
import type { AnalysisResult } from "../types/analysis";
import { METRIC_REGISTRY } from "./metricRegistry";

export interface AnalysisSummary {
  rating: string | undefined;
  readinessScore: number | undefined;
  detectionRate: number | undefined;
  cameraView: string | undefined;
  biomechanicsReady: boolean;
  bodyVisibility: number | undefined;
  movementQuality: number | undefined;
  provider: string | undefined;
}

const READINESS_METRIC = METRIC_REGISTRY.find((m) => m.key === "readiness_score")!;
const DETECTION_METRIC = METRIC_REGISTRY.find((m) => m.key === "detection_rate")!;
const BODY_VISIBILITY_METRIC = METRIC_REGISTRY.find((m) => m.key === "body_visibility")!;
const MOVEMENT_QUALITY_METRIC = METRIC_REGISTRY.find((m) => m.key === "movement_quality")!;

export function extractAnalysisSummary(analysisResult: unknown): AnalysisSummary | null {
  if (!analysisResult || typeof analysisResult !== "object") return null;
  const result = analysisResult as AnalysisResult;
  const quality = result.recording_quality as any;

  return {
    rating: quality?.rating,
    readinessScore: READINESS_METRIC.accessor(result)?.value,
    detectionRate: DETECTION_METRIC.accessor(result)?.value,
    cameraView: quality?.camera_view?.classification,
    biomechanicsReady: (result.biomechanics as any)?.status !== "skipped",
    bodyVisibility: BODY_VISIBILITY_METRIC.accessor(result)?.value,
    movementQuality: MOVEMENT_QUALITY_METRIC.accessor(result)?.value,
    provider: result.provider,
  };
}

// Shared date formatting - the same "en-IN, day/short-month/year" format
// already independently written in PerformanceDetail.tsx, AthleteReports.tsx,
// AthleteProgress.tsx, and PartnerAthleteDetail.tsx. New callers (the
// Twin components) use this one; existing call sites are left as-is.
export function formatSessionDate(date?: string | null): string {
  if (!date) return "Date unavailable";
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}
