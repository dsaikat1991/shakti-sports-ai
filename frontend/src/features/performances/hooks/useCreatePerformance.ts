import { useMutation } from "@tanstack/react-query";
import {
  createPerformanceRecord,
  uploadPerformanceRecording,
} from "../services/performance.service";
import {
  submitVideoForAnalysis,
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
        const job = await submitVideoForAnalysis(draft.recording);

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