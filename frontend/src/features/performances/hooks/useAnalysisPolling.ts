import { useEffect, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { getAnalysisStatus, updatePerformanceAnalysis } from "../services/analysis.service";
import type { AnalysisJob } from "../types/analysis";

const POLL_INTERVAL_MS = 3000;

// Real jobs have taken up to ~220s cold (worst case, GPU worker not yet
// warm - see docs/ENGINEERING_HANDOFF.md section 7). This is a generous
// upper bound beyond that, not a typical duration - past this we stop
// polling client-side rather than poll forever against a stuck/crashed
// backend. We deliberately do NOT write "failed" to Supabase on timeout:
// the backend job may still finish later, and a client-side timeout
// isn't evidence the job itself failed.
const MAX_POLL_DURATION_MS = 10 * 60 * 1000;

export function useAnalysisPolling(performanceId?: string, jobId?: string | null) {
  const queryClient = useQueryClient();
  const startedAtRef = useRef<number | null>(null);
  const persistedTerminalStateRef = useRef<string | null>(null);

  useEffect(() => {
    startedAtRef.current = jobId ? Date.now() : null;
    persistedTerminalStateRef.current = null;
  }, [jobId]);

  const query = useQuery<AnalysisJob>({
    queryKey: ["analysis-job", jobId],
    queryFn: () => getAnalysisStatus(jobId as string),
    enabled: Boolean(jobId),
    // react-query stops calling this (and therefore stops polling) once
    // the query becomes inactive - which happens automatically when the
    // component using this hook unmounts. Terminal status and the
    // elapsed-time timeout below are the other two stop conditions.
    refetchInterval: (latest) => {
      const status = latest.state.data?.status;
      if (status === "completed" || status === "failed") {
        return false;
      }

      const startedAt = startedAtRef.current;
      if (startedAt && Date.now() - startedAt > MAX_POLL_DURATION_MS) {
        return false;
      }

      return POLL_INTERVAL_MS;
    },
  });

  const status = query.data?.status;
  const elapsedBeyondTimeout =
    Boolean(startedAtRef.current) &&
    Date.now() - (startedAtRef.current as number) > MAX_POLL_DURATION_MS;
  const timedOut =
    Boolean(jobId) &&
    status !== "completed" &&
    status !== "failed" &&
    elapsedBeyondTimeout;

  useEffect(() => {
    if (!performanceId || !jobId || !query.data) return;
    if (status !== "completed" && status !== "failed") return;

    // StrictMode double-invokes effects in dev; without this guard the
    // same terminal write could fire twice for one job. Keyed on jobId so
    // a genuinely new job (e.g. after a retry) isn't blocked by a stale
    // guard from a previous one.
    const guardKey = `${jobId}:${status}`;
    if (persistedTerminalStateRef.current === guardKey) return;
    persistedTerminalStateRef.current = guardKey;

    if (status === "completed") {
      updatePerformanceAnalysis(performanceId, {
        upload_status: "completed",
        analysis_result: query.data.result,
      }).then(() =>
        queryClient.invalidateQueries({
          queryKey: ["performance", performanceId],
        }),
      );
    } else {
      updatePerformanceAnalysis(performanceId, {
        upload_status: "failed",
        analysis_error: query.data.error ?? "Analysis failed.",
      }).then(() =>
        queryClient.invalidateQueries({
          queryKey: ["performance", performanceId],
        }),
      );
    }
    // Intermediate queued/processing states are shown live from `query`
    // directly (see PerformanceProcessing.tsx) - only terminal outcomes
    // are worth a Supabase round-trip.
  }, [status, performanceId, jobId, query.data, queryClient]);

  return { ...query, timedOut };
}
