import { useMutation } from "@tanstack/react-query";
import {
  createPerformanceRecord,
  uploadPerformanceRecording,
} from "../services/performance.service";
import {
  startAnalysisForStoredVideo,
  updatePerformanceAnalysis,
} from "../services/analysis.service";
import type { PerformanceDraft } from "../types/performance";

type CreatePerformanceInput = {
  athleteId: string;
  draft: PerformanceDraft;
};

export function useCreatePerformance() {
  return useMutation({
    mutationFn: async ({ athleteId, draft }: CreatePerformanceInput) => {
      if (!draft.recording) {
        throw new Error("Please upload a recording first.");
      }

      const { data: uploadData, error: uploadError } =
        await uploadPerformanceRecording(athleteId, draft.recording);

      if (uploadError || !uploadData) {
        throw new Error(uploadError?.message || "Recording upload failed.");
      }

      const { data, error } = await createPerformanceRecord(
        athleteId,
        draft,
        uploadData.path,
      );

     if (error || !data) {
        throw new Error(error?.message || "Performance could not be created.");
     }

      try {
        // Signed-URL submission, not a second browser upload: the video
        // already sits in Storage from the step above, so the backend
        // downloads it itself instead of the browser sending the same
        // bytes twice. This also means the exact same path is reused for
        // retrying analysis later (see useRetryAnalysis), without needing
        // the original File object still in memory.
        const job = await startAnalysisForStoredVideo(uploadData.path);

        await updatePerformanceAnalysis(data.id, {
          upload_status: "analyzing",
          analysis_job_id: job.job_id,
        });
      } catch (analysisError) {
        // The performance record already exists in Supabase - a backend
        // outage (e.g. the RTMPose worker isn't running) shouldn't fail
        // the whole upload, just leave AI analysis unavailable for it.
        await updatePerformanceAnalysis(data.id, {
          upload_status: "failed",
          analysis_error:
            analysisError instanceof Error
              ? analysisError.message
              : "Could not start analysis.",
        });
      }

      return data;
    },
  });
}
