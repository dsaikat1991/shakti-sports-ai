import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { getAnalysisStatus, updatePerformanceAnalysis } from "../services/analysis.service";
import type { AnalysisJob } from "../types/analysis";

const POLL_INTERVAL_MS = 3000;

// Polls the FastAPI backend for job status while a job is in flight, and
// persists the terminal outcome (completed/failed) back onto the Supabase
// performances row so it's visible on reload without needing the backend's
// in-memory job store, which does not survive a server restart.
export function useAnalysisPolling(performanceId?: string, jobId?: string | null) {
  const queryClient = useQueryClient();

  const query = useQuery<AnalysisJob>({
    queryKey: ["analysis-job", jobId],
    queryFn: () => getAnalysisStatus(jobId as string),
    enabled: Boolean(jobId),
    refetchInterval: (latest) => {
      const status = latest.state.data?.status;
      return status === "completed" || status === "failed"
        ? false
        : POLL_INTERVAL_MS;
    },
  });

  const status = query.data?.status;

  useEffect(() => {
    if (!performanceId || !query.data) return;

    if (status === "completed") {
      updatePerformanceAnalysis(performanceId, {
        upload_status: "completed",
        analysis_result: query.data.result,
      }).then(() =>
        queryClient.invalidateQueries({
          queryKey: ["performance", performanceId],
        }),
      );
    } else if (status === "failed") {
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
  }, [status, performanceId, query.data, queryClient]);

  return query;
}
