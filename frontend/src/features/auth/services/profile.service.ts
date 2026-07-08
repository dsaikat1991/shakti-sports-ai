import { supabase } from "../../../lib/supabase";
import type { UserRole } from "../types/auth";

type CreateBaseProfileInput = {
  id: string;
  email: string;
  role: UserRole;
  fullName: string;
  state?: string;
  district?: string;
};

type CreateAthleteProfileInput = {
  id: string;
  dateOfBirth: string;
  gender: string;
  preferredEvent: string;
  academy?: string;
};

export async function createBaseProfile(input: CreateBaseProfileInput) {
  return supabase.from("profiles").insert({
    id: input.id,
    email: input.email,
    role: input.role,
    full_name: input.fullName,
    state: input.state,
    district: input.district,
  });
}

export async function createAthleteProfile(input: CreateAthleteProfileInput) {
  return supabase.from("athlete_profiles").insert({
    id: input.id,
    date_of_birth: input.dateOfBirth || null,
    gender: input.gender || null,
    preferred_event: input.preferredEvent,
    academy: input.academy || null,
  });
}