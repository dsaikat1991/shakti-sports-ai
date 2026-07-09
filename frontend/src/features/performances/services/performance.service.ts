import { supabase } from "../../../lib/supabase";
import type { PerformanceDraft, PerformanceEvent } from "../types/performance";

const BUCKET_NAME = "performance-recordings";

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

return supabase
  .from("performances")
  .insert({
    athlete_id: athleteId,
    event_id: eventData.id,
    title: draft.title,
    performance_date: draft.performedOn,
    attempt_number: 1,
    video_url: videoPath,
    upload_status: "uploaded",
    notes: draft.notes || null,
  })
  .select("id")
  .single();
}
export async function getAthletePerformances(athleteId: string) {
  return supabase
    .from("performances")
    .select(
      `
      id,
      title,
      performance_date,
      upload_status,
      video_url,
      notes,
      created_at,
      events (
        name,
        category
      )
    `,
    )
    .eq("athlete_id", athleteId)
    .order("created_at", { ascending: false });
}