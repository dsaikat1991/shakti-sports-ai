import type { PerformanceType } from "../types/performance";

const PERFORMANCE_TYPE_LABELS: Record<PerformanceType, string> = {
  practice: "Practice",
  competition: "Competition",
  trial: "Trial",
  assessment: "Assessment",
};

// Event and date are already shown as their own line in every view that
// displays a performance (AthleteHome, PerformanceHistory, PerformanceDetail,
// PartnerAthleteDetail, the Digital Twin timeline) - repeating them here
// would just duplicate that line. This composes the one piece of structured
// metadata that currently has no display anywhere (performance_type) with
// the athlete's own optional personal text, instead of forcing a manual
// "session name" decision or fabricating a fuller sentence.
export function buildPerformanceDisplayName(performance: {
  performance_type?: string | null;
  title?: string | null;
}): string {
  const typeLabel =
    (performance.performance_type &&
      PERFORMANCE_TYPE_LABELS[performance.performance_type as PerformanceType]) ||
    "Session";

  const personalNote = performance.title?.trim();

  return personalNote ? `${typeLabel} — "${personalNote}"` : typeLabel;
}
