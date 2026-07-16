import { supabase } from "../../../lib/supabase";
import type { PerformanceDraft, PerformanceEvent } from "../types/performance";

export const BUCKET_NAME = "performance-recordings";

const EVENT_NAME_MAP: Record<PerformanceEvent, string> = {
  "100m": "Sprint",
  "110h": "Hurdles",
  long_jump: "Long Jump",
  high_jump: "High Jump",
};

export async function uploadPerformanceRecording(
  athleteId: string,
  file: File,
) {
  const fileExt = file.name.split(".").pop();
  const filePath = `${athleteId}/${crypto.randomUUID()}.${fileExt}`;

  return supabase.storage.from(BUCKET_NAME).upload(filePath, file, {
    cacheControl: "3600",
    upsert: false,
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

  return supabase
    .from("performances")
    .insert({
      athlete_id: athleteId,
      event_id: eventData.id,
      performance_number: nextPerformanceNumber,
      title: draft.title,
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