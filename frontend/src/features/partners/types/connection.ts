export type ConnectionStatus = "pending" | "accepted" | "rejected" | "revoked";
export type ConnectionInitiator = "coach" | "athlete";
export type PartnerRole = "coach" | "academy";

export interface PartnerConnection {
  id: string;
  coach_id: string;
  athlete_id: string;
  partner_role: PartnerRole;
  status: ConnectionStatus;
  initiated_by: ConnectionInitiator;
  invited_email: string | null;
  requested_at: string;
  responded_at: string | null;
  created_at: string;
}

export interface BaseProfile {
  id: string;
  full_name: string | null;
  email: string | null;
  role: string | null;
}

export interface CoachProfileSummary {
  id: string;
  organization: string | null;
  designation: string | null;
  specialization: string | null;
}

export interface AcademyProfileSummary {
  id: string;
  academy_name: string | null;
  address: string | null;
  website: string | null;
}

export interface AthleteProfileSummary {
  id: string;
  date_of_birth: string | null;
  gender: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  preferred_event: string | null;
  secondary_event: string | null;
  academy: string | null;
  bio: string | null;
  personal_best: string | null;
}

export interface CoachNote {
  id: string;
  note: string;
  created_at: string;
  updated_at: string;
}
