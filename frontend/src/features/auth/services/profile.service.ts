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

type CreateCoachProfileInput = {
  id: string;
  organization?: string;
  designation?: string;
  experienceYears?: number;
  specialization?: string;
  bio?: string;
};

type CreateAcademyProfileInput = {
  id: string;
  academyName?: string;
  address?: string;
  website?: string;
  description?: string;
};

// upsert, not insert: the RequireNoRole route guard should prevent an
// already-onboarded user from ever reaching this a second time, but
// making the write itself idempotent is a cheap, real safety net - a
// plain insert crashes with a raw profiles_pkey duplicate-key violation
// if it's ever reached anyway (confirmed live via Google OAuth, whose
// redirectTo previously sent every login, new or returning, through
// onboarding - see RequireNoRole.tsx).
export async function createBaseProfile(input: CreateBaseProfileInput) {
  return supabase.from("profiles").upsert({
    id: input.id,
    email: input.email,
    role: input.role,
    full_name: input.fullName,
    state: input.state,
    district: input.district,
  });
}

export async function createAthleteProfile(input: CreateAthleteProfileInput) {
  return supabase.from("athlete_profiles").upsert({
    id: input.id,
    date_of_birth: input.dateOfBirth || null,
    gender: input.gender || null,
    preferred_event: input.preferredEvent,
    academy: input.academy || null,
  });
}

export async function createCoachProfile(input: CreateCoachProfileInput) {
  return supabase.from("coach_profiles").upsert({
    id: input.id,
    organization: input.organization || null,
    designation: input.designation || null,
    experience_years: input.experienceYears ?? null,
    specialization: input.specialization || null,
    bio: input.bio || null,
  });
}

export async function createAcademyProfile(input: CreateAcademyProfileInput) {
  return supabase.from("academy_profiles").upsert({
    id: input.id,
    academy_name: input.academyName || null,
    address: input.address || null,
    website: input.website || null,
    description: input.description || null,
  });
}

// Fetches role directly rather than relying on AuthContext's role state,
// which updates asynchronously off a separate effect - reading it
// immediately after a sign-in call would risk a stale/null value.
export async function getUserRole(userId: string): Promise<UserRole | null> {
  const { data } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", userId)
    .maybeSingle();

  return (data?.role as UserRole | undefined) ?? null;
}