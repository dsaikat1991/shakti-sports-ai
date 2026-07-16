import { supabase } from "../../../lib/supabase";

const CONNECTION_COLUMNS =
  "id, coach_id, athlete_id, partner_role, status, initiated_by, invited_email, requested_at, responded_at, created_at";

// Wraps request_partner_connection() (see supabase/migrations/0005) -
// the only way to create a connection row. Resolves the target account
// by email server-side so neither party ever needs direct SELECT access
// to a stranger's profile just to invite them. Every failure path on
// the database side raises the same generic message by design (no
// account, wrong role, already connected) - surfaced here as-is rather
// than parsed into more specific client-side copy.
export async function requestPartnerConnection(targetEmail: string) {
  const { data, error } = await supabase.rpc("request_partner_connection", {
    target_email: targetEmail,
  });

  if (error) {
    throw new Error(error.message);
  }

  return data as string;
}

export async function getConnectionsForCoach(coachId: string) {
  return supabase
    .from("coach_athlete_connections")
    .select(CONNECTION_COLUMNS)
    .eq("coach_id", coachId)
    .order("created_at", { ascending: false });
}

export async function getConnectionsForAthlete(athleteId: string) {
  return supabase
    .from("coach_athlete_connections")
    .select(CONNECTION_COLUMNS)
    .eq("athlete_id", athleteId)
    .order("created_at", { ascending: false });
}

export async function respondToConnection(
  connectionId: string,
  status: "accepted" | "rejected",
) {
  return supabase
    .from("coach_athlete_connections")
    .update({ status })
    .eq("id", connectionId)
    .select(CONNECTION_COLUMNS)
    .single();
}

export async function revokeConnection(connectionId: string) {
  return supabase
    .from("coach_athlete_connections")
    .update({ status: "revoked" })
    .eq("id", connectionId)
    .select(CONNECTION_COLUMNS)
    .single();
}

// RLS gates every one of these to exactly what the caller is currently
// allowed to see (see migration 0005) - a coach only gets a row back for
// an athlete once a matching pending-received or accepted connection
// exists, and vice versa. No client-side filtering needed on top.
export async function getProfilesByIds(ids: string[]) {
  if (ids.length === 0) return { data: [], error: null };

  return supabase.from("profiles").select("id, full_name, email, role").in("id", ids);
}

export async function getCoachProfilesByIds(ids: string[]) {
  if (ids.length === 0) return { data: [], error: null };

  return supabase
    .from("coach_profiles")
    .select("id, organization, designation, specialization")
    .in("id", ids);
}

export async function getAcademyProfilesByIds(ids: string[]) {
  if (ids.length === 0) return { data: [], error: null };

  return supabase
    .from("academy_profiles")
    .select("id, academy_name, address, website")
    .in("id", ids);
}

export async function getAthleteProfile(athleteId: string) {
  return supabase
    .from("athlete_profiles")
    .select(
      "id, date_of_birth, gender, height_cm, weight_kg, preferred_event, secondary_event, academy, bio, personal_best",
    )
    .eq("id", athleteId)
    .maybeSingle();
}

// Deliberately omits video_url. A coach's RLS grant is SELECT-only on
// performances (see migration 0005), and storage RLS separately blocks
// them from ever signing that path - so this isn't fixing an active
// leak - but there's no reason the raw storage path should even land in
// a coach's query cache when nothing here renders it. Athlete-owned
// reads still use the full getAthletePerformances/getPerformanceById in
// performance.service.ts, which do need video_url for playback/retry.
const CONNECTED_PERFORMANCE_COLUMNS = `
  id,
  performance_number,
  title,
  performance_date,
  upload_status,
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
`;

export async function getConnectedAthletePerformances(athleteId: string) {
  return supabase
    .from("performances")
    .select(CONNECTED_PERFORMANCE_COLUMNS)
    .eq("athlete_id", athleteId)
    .order("created_at", { ascending: false });
}

export async function getConnectedPerformanceById(performanceId: string) {
  return supabase
    .from("performances")
    .select(CONNECTED_PERFORMANCE_COLUMNS)
    .eq("id", performanceId)
    .single();
}

export async function getNotesForConnection(connectionId: string) {
  return supabase
    .from("coach_athlete_notes")
    .select("id, note, created_at, updated_at")
    .eq("connection_id", connectionId)
    .order("created_at", { ascending: false });
}

export async function addNote(connectionId: string, coachId: string, note: string) {
  return supabase
    .from("coach_athlete_notes")
    .insert({ connection_id: connectionId, coach_id: coachId, note })
    .select("id, note, created_at, updated_at")
    .single();
}

export async function deleteNote(noteId: string) {
  return supabase.from("coach_athlete_notes").delete().eq("id", noteId);
}
