import { useMutation } from "@tanstack/react-query";
import {
  createPerformanceRecord,
  uploadPerformanceRecording,
} from "../services/performance.service";
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
      return data;
    },
  });
}