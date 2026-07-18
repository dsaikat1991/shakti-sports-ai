import { supabase, supabaseUrl, supabasePublishableKey } from "../../../lib/supabase";
import type { PerformanceDraft, PerformanceEvent } from "../types/performance";

export const BUCKET_NAME = "performance-recordings";

const EVENT_NAME_MAP: Record<PerformanceEvent, string> = {
  "100m": "Sprint",
  "110h": "Hurdles",
  long_jump: "Long Jump",
  high_jump: "High Jump",
};

type UploadResult =
  | { data: { path: string }; error: null }
  | { data: null; error: Error };

// supabase-js's storage.upload() has no upload-progress callback (it's a
// thin wrapper around fetch), so a real progress bar needs a raw XHR
// request to the same Storage REST endpoint instead - mirroring exactly
// what storage-js itself sends (FormData with a cacheControl field plus
// the file under an empty field name, x-upsert header) so the request is
// interpreted identically by the server.
export async function uploadPerformanceRecording(
  athleteId: string,
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadResult> {
  const fileExt = file.name.split(".").pop();
  const filePath = `${athleteId}/${crypto.randomUUID()}.${fileExt}`;

  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    return { data: null, error: new Error("Your session has expired.") };
  }

  const formData = new FormData();
  formData.append("cacheControl", "3600");
  formData.append("", file);

  return new Promise((resolve) => {
    const xhr = new XMLHttpRequest();

    xhr.open(
      "POST",
      `${supabaseUrl}/storage/v1/object/${BUCKET_NAME}/${filePath}`,
    );
    xhr.setRequestHeader("Authorization", `Bearer ${session.access_token}`);
    xhr.setRequestHeader("apikey", supabasePublishableKey);
    xhr.setRequestHeader("x-upsert", "false");

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        onProgress?.(100);
        resolve({ data: { path: filePath }, error: null });
        return;
      }

      let message = "Recording upload failed.";
      try {
        const parsed = JSON.parse(xhr.responseText);
        message = parsed.message || parsed.error || message;
      } catch {
        // Non-JSON error body - fall back to the generic message above.
      }
      resolve({ data: null, error: new Error(message) });
    };

    xhr.onerror = () => {
      resolve({
        data: null,
        error: new Error("Recording upload failed. Check your connection."),
      });
    };

    xhr.send(formData);
  });
}

async function getEventId(event: PerformanceEvent) {
  const eventName = EVENT_NAME_MAP[event];

  return supabase
    .from("events")
    .select("id")
    .eq("name", eventName)
    .single();
}

async function getNextPerformanceNumber(athleteId: string) {
  const { count, error } = await supabase
    .from("performances")
    .select("id", { count: "exact", head: true })
    .eq("athlete_id", athleteId);

  if (error) {
    throw new Error(error.message);
  }

  return (count ?? 0) + 1;
}

export async function createPerformanceRecord(
  athleteId: string,
  draft: PerformanceDraft,
  videoPath: string,
) {
  if (!draft.event) {
    throw new Error("Performance event is required.");
  }

  const { data: eventData, error: eventError } = await getEventId(draft.event);

  if (eventError || !eventData) {
    throw new Error(eventError?.message || "Could not find selected event.");
  }

  const nextPerformanceNumber = await getNextPerformanceNumber(athleteId);

  // title is purely optional personal text now - stored as-is (may be
  // empty). The display name shown to users is composed at read time from
  // performance_type + this personal text (see lib/performanceDisplayName.ts),
  // not baked into a stored string here.
  return supabase
    .from("performances")
    .insert({
      athlete_id: athleteId,
      event_id: eventData.id,
      performance_number: nextPerformanceNumber,
      title: draft.title.trim(),
      performance_type: draft.performanceType ?? null,
      performance_date: draft.performedOn,
      attempt_number: 1,
      video_url: videoPath,
      upload_status: "uploaded",
      notes: draft.notes || null,
    })
    .select("id, performance_number")
    .single();
}

export async function getAthletePerformances(athleteId: string) {
  return supabase
    .from("performances")
    .select(
      `
      id,
      performance_number,
      title,
      performance_type,
      performance_date,
      upload_status,
      video_url,
      notes,
      created_at,
      updated_at,
      analysis_job_id,
      analysis_error,
      analysis_result,
      events (
        name,
        category
      )
    `,
    )
    .eq("athlete_id", athleteId)
    .order("created_at", { ascending: false });
}

export async function getPerformanceById(performanceId: string) {
  return supabase
    .from("performances")
    .select(
      `
      id,
      performance_number,
      title,
      performance_type,
      performance_date,
      upload_status,
      video_url,
      notes,
      created_at,
      analysis_job_id,
      analysis_result,
      analysis_error,
      events (
        name,
        category
      )
    `,
    )
    .eq("id", performanceId)
    .single();
}