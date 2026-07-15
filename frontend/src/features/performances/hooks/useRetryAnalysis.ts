import { useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  startAnalysisForStoredVideo,
  updatePerformanceAnalysis,
} from "../services/analysis.service";

type RetryAnalysisInput = {
  performanceId: string;
  videoPath: string;
};

// Re-submits an already-uploaded performance's video for analysis. Only
// meaningful from a "failed" state (see PerformanceDetail/Processing) -
// re-mints a signed URL for the same Storage object rather than needing
// the original browser File object, which is why this is possible at all
// from a page like performance history where that File was never held.
export function useRetryAnalysis() {
  const queryClient = useQueryClient();
  // Same synchronous-lock reasoning as ReviewStep's submission guard:
  // mutation.isPending only updates on the next render, so a fast
  // double-click on "Retry" can otherwise start two jobs for one
  // performance before the button visually disables.
  const inFlightRef = useRef(false);

  const mutation = useMutation({
    mutationFn: async ({ performanceId, videoPath }: RetryAnalysisInput) => {
      const job = await startAnalysisForStoredVideo(videoPath);

      await updatePerformanceAnalysis(performanceId, {
        upload_status: "analyzing",
        analysis_job_id: job.job_id,
        analysis_error: null,
        analysis_result: null,
      });

      return job;
    },
    onSuccess: (_job, { performanceId }) => {
      queryClient.invalidateQueries({
        queryKey: ["performance", performanceId],
      });
    },
    onSettled: () => {
      inFlightRef.current = false;
    },
  });

  function retry(input: RetryAnalysisInput) {
    if (inFlightRef.current) return;
    inFlightRef.current = true;
    mutation.mutate(input);
  }

  return { ...mutation, retry };
}
