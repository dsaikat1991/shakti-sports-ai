import type { AnalysisResult } from "../types/analysis";
import { METRIC_REGISTRY } from "./metricRegistry";
import { extractAnalysisSummary } from "./analysisSummary";

// Picks the single most meaningful real finding to lead the Sprint Report
// with, instead of echoing back whatever the athlete typed as a session
// name. Priority order favours the metrics with the broadest, most
// immediately understandable meaning (production-status, not experimental).
const HEADLINE_PRIORITY: {
  key: string;
  phrase: (formatted: string) => string;
}[] = [
  { key: "cadence", phrase: (v) => `Your cadence held steady at ${v}` },
  { key: "stride_frequency", phrase: (v) => `Your stride frequency was ${v}` },
  { key: "knee_symmetry", phrase: (v) => `Your knee symmetry scored ${v}` },
];

// Returns null when there is nothing honest to lead with yet (analysis
// still running, or biomechanics was skipped) - the caller falls back to
// the plain session title rather than fabricating a finding.
export function buildReportHeadline(analysisResult: unknown): string | null {
  const summary = extractAnalysisSummary(analysisResult);
  if (!summary || !summary.biomechanicsReady) return null;

  const result = analysisResult as AnalysisResult;

  for (const { key, phrase } of HEADLINE_PRIORITY) {
    const metric = METRIC_REGISTRY.find((m) => m.key === key);
    if (!metric) continue;

    const extracted = metric.accessor(result);
    if (!extracted) continue;

    return phrase(metric.format(extracted));
  }

  return null;
}
