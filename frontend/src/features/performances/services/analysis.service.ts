import { supabase } from "../../../lib/supabase";
import { BUCKET_NAME } from "./performance.service";
import type { AnalysisJob, AnalysisResult } from "../types/analysis";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined;

// Long enough for the backend to download a large clip over a slow
// connection; short enough that a leaked URL (logs, browser history)
// isn't useful for long. The backend also validates the URL's host/path
// before using it - see backend/app/api/routes.py.
const SIGNED_URL_EXPIRY_SECONDS = 600;

function requireApiBaseUrl(): string {
  if (!API_BASE_URL) {
    throw new Error(
      "VITE_API_BASE_URL is not configured - cannot reach the analysis backend.",
    );
  }
  return API_BASE_URL;
}

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

// Mints a short-lived signed URL for a video already sitting in the
// (private) performance-recordings bucket, so the backend can download it
// itself instead of the browser re-uploading the same bytes a second
// time. Storage RLS still gates who can call this - only the owning
// athlete's session can sign a URL for their own object path.
export async function createSignedVideoUrl(storagePath: string): Promise<string> {
  const { data, error } = await supabase.storage
    .from(BUCKET_NAME)
    .createSignedUrl(storagePath, SIGNED_URL_EXPIRY_SECONDS);

  if (error || !data?.signedUrl) {
    throw new Error(error?.message || "Could not create a signed video URL.");
  }

  return data.signedUrl;
}

export async function submitVideoUrlForAnalysis(
  videoUrl: string,
): Promise<{ job_id: string; status: string }> {
  const response = await fetch(`${requireApiBaseUrl()}/api/analyze/video-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_url: videoUrl }),
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  return response.json();
}

export async function getAnalysisStatus(jobId: string): Promise<AnalysisJob> {
  const response = await fetch(
    `${requireApiBaseUrl()}/api/analyze/video/${jobId}`,
  );

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  return response.json();
}

// Matches the performances.upload_status CHECK constraint in Supabase,
// which allows exactly: uploaded, analyzing, completed, failed.
type AnalysisUpdate = {
  upload_status: "analyzing" | "completed" | "failed";
  analysis_job_id?: string | null;
  analysis_result?: AnalysisResult | null;
  analysis_error?: string | null;
};

export async function updatePerformanceAnalysis(
  performanceId: string,
  update: AnalysisUpdate,
) {
  // .update() with an explicit column set only ever touches those
  // columns - video_url, notes, title, etc. on this row are untouched,
  // and RLS (auth.uid() = athlete_id) still applies to this request same
  // as any other authenticated client call.
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

// Shared by first-time submission (useCreatePerformance) and retry
// (usePerformance's retry action): mint a signed URL for the given
// storage path and hand it to the backend, returning the new job id.
export async function startAnalysisForStoredVideo(
  storagePath: string,
): Promise<{ job_id: string; status: string }> {
  const signedUrl = await createSignedVideoUrl(storagePath);
  return submitVideoUrlForAnalysis(signedUrl);
}
