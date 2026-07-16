import { supabase } from "../../../lib/supabase";

export interface AthleteBaseProfile {
  id: string;
  full_name: string | null;
  email: string | null;
  state: string | null;
  district: string | null;
  avatar_url: string | null;
}

export interface AthleteSportingProfile {
  id: string;
  date_of_birth: string | null;
  gender: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  preferred_event: string | null;
  secondary_event: string | null;
  academy: string | null;
  bio: string | null;
  dominant_leg: string | null;
  personal_best: string | null;
  achievements: string | null;
  ai_training_consent: boolean;
  deletion_requested_at: string | null;
}

export type BaseProfileUpdate = Partial<
  Pick<AthleteBaseProfile, "full_name" | "state" | "district">
>;

export type SportingProfileUpdate = Partial<
  Pick<
    AthleteSportingProfile,
    | "date_of_birth"
    | "gender"
    | "height_cm"
    | "weight_kg"
    | "preferred_event"
    | "secondary_event"
    | "academy"
    | "bio"
    | "dominant_leg"
    | "personal_best"
    | "achievements"
  >
>;

export async function getBaseProfile(athleteId: string) {
  return supabase
    .from("profiles")
    .select("id, full_name, email, state, district, avatar_url")
    .eq("id", athleteId)
    .maybeSingle();
}

export async function getSportingProfile(athleteId: string) {
  return supabase
    .from("athlete_profiles")
    .select(
      "id, date_of_birth, gender, height_cm, weight_kg, preferred_event, secondary_event, academy, bio, dominant_leg, personal_best, achievements, ai_training_consent, deletion_requested_at",
    )
    .eq("id", athleteId)
    .maybeSingle();
}

export async function updateBaseProfile(athleteId: string, fields: BaseProfileUpdate) {
  return supabase.from("profiles").update(fields).eq("id", athleteId);
}

export async function updateSportingProfile(
  athleteId: string,
  fields: SportingProfileUpdate,
) {
  return supabase.from("athlete_profiles").update(fields).eq("id", athleteId);
}

export async function updateAiTrainingConsent(athleteId: string, consent: boolean) {
  return supabase
    .from("athlete_profiles")
    .update({ ai_training_consent: consent })
    .eq("id", athleteId);
}

// Records intent only - does not delete anything. No backend cascade-delete
// endpoint exists yet; a real deletion is reviewed and actioned manually.
// Setting this back to null is how a request gets withdrawn.
export async function setAccountDeletionRequested(athleteId: string, requested: boolean) {
  return supabase
    .from("athlete_profiles")
    .update({ deletion_requested_at: requested ? new Date().toISOString() : null })
    .eq("id", athleteId);
}
