import { supabase } from "../../../lib/supabase";
import type { AnalysisJob, AnalysisResult } from "../types/analysis";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined;

async function parseErrorDetail(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") {
      return body.detail;
    }
  } catch {
    // response body wasn't JSON - fall through to the generic message
  }

  return `Backend request failed with status ${response.status}.`;
}

export async function submitVideoForAnalysis(
  file: File,
): Promise<{ job_id: string; status: string }> {
  if (!API_BASE_URL) {
    throw new Error(
      "VITE_API_BASE_URL is not configured - cannot reach the analysis backend.",
    );
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/analyze/video`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  return response.json();
}

export async function getAnalysisStatus(jobId: string): Promise<AnalysisJob> {
  if (!API_BASE_URL) {
    throw new Error(
      "VITE_API_BASE_URL is not configured - cannot reach the analysis backend.",
    );
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze/video/${jobId}`);

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  return response.json();
}

// Matches the performances.upload_status CHECK constraint in Supabase,
// which allows exactly: uploaded, analyzing, completed, failed.
type AnalysisUpdate = {
  upload_status: "analyzing" | "completed" | "failed";
  analysis_job_id?: string;
  analysis_result?: AnalysisResult | null;
  analysis_error?: string | null;
};

export async function updatePerformanceAnalysis(
  performanceId: string,
  update: AnalysisUpdate,
) {
  const result = await supabase
    .from("performances")
    .update(update)
    .eq("id", performanceId);

  if (result.error) {
    // Failures here are easy to miss (nothing else surfaces them to the
    // user), and previously failed silently against a CHECK constraint -
    // always log so a bad status value is visible in the console instead
    // of just leaving the row stuck on its previous status.
    console.error("Failed to update performance analysis state:", result.error);
  }

  return result;
}
