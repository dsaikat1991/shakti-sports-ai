// Mirrors the FastAPI backend's contract for POST/GET /api/analyze/video.
// See docs/ENGINEERING_HANDOFF.md section 6 for the authoritative shape.

export type AnalysisJobStatus = "queued" | "processing" | "completed" | "failed";

export interface AnalysisResult {
  provider: string;
  video: {
    total_frames: number;
    fps: number;
    duration_seconds: number;
  };
  analysis: {
    frames_with_pose: number;
    detection_rate_percent: number;
  };
  recording_quality: Record<string, unknown>;
  tracking_summary: Record<string, unknown>;
  biomechanics:
    | { status: "skipped"; reason: string }
    | Record<string, unknown>;
}

export interface AnalysisJob {
  job_id: string;
  status: AnalysisJobStatus;
  created_at?: string;
  updated_at?: string;
  result: AnalysisResult | null;
  error: string | null;
}
