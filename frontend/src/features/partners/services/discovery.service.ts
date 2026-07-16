import { supabase } from "../../../lib/supabase";

export interface DiscoveredAthlete {
  athlete_id: string;
  full_name: string;
  preferred_event: string | null;
  secondary_event: string | null;
  state: string | null;
}

// Wraps search_discoverable_athletes() (migration 0009). Returns an
// empty array both for "no matches" and "you're not entitled to search"
// - deliberately indistinguishable, see the migration's own comment on
// why (no oracle for entitlement status). Requires at least one filter
// server-side; the RPC raises if both are null, surfaced as-is.
export async function searchDiscoverableAthletes(filters: {
  event?: string | null;
  state?: string | null;
  limit?: number;
  offset?: number;
}) {
  const { data, error } = await supabase.rpc("search_discoverable_athletes", {
    p_event: filters.event ?? null,
    p_state: filters.state ?? null,
    p_limit: filters.limit ?? 20,
    p_offset: filters.offset ?? 0,
  });

  if (error) throw new Error(error.message);
  return (data ?? []) as DiscoveredAthlete[];
}

// Wraps request_partner_connection_by_athlete_id() (migration 0009) -
// the discovery-flow equivalent of requestPartnerConnection(email) in
// connections.service.ts. Never needs/exposes the target's email.
export async function requestConnectionByAthleteId(targetAthleteId: string) {
  const { data, error } = await supabase.rpc("request_partner_connection_by_athlete_id", {
    target_athlete_id: targetAthleteId,
  });

  if (error) throw new Error(error.message);
  return data as string;
}

export interface BookmarkedAthleteCard {
  bookmark_id: string;
  athlete_id: string;
  full_name: string | null;
  preferred_event: string | null;
  secondary_event: string | null;
  state: string | null;
  visible: boolean;
}

// Wraps get_bookmarked_athlete_cards() (migration 0010) - the ONLY
// supported read path for bookmark display data. Never join
// coach_athlete_bookmarks straight to profiles/athlete_profiles from
// the client - a withdrawn athlete's card must come back with
// visible: false and every field null, which this RPC guarantees and a
// raw client-side join would not.
export async function getBookmarkedAthleteCards() {
  const { data, error } = await supabase.rpc("get_bookmarked_athlete_cards");
  if (error) throw new Error(error.message);
  return (data ?? []) as BookmarkedAthleteCard[];
}

export async function createBookmark(coachId: string, athleteId: string) {
  return supabase
    .from("coach_athlete_bookmarks")
    .insert({ coach_id: coachId, athlete_id: athleteId })
    .select("id")
    .single();
}

export async function removeBookmark(bookmarkId: string) {
  return supabase.from("coach_athlete_bookmarks").delete().eq("id", bookmarkId);
}

export type ListType = "TOURNAMENT_SELECTION" | "CAMP_SELECTION" | "TRIAL_SELECTION" | "TEAM_SQUAD";

export interface CoachAthleteList {
  id: string;
  owner_id: string;
  name: string;
  list_type: ListType;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export async function getLists(ownerId: string) {
  return supabase
    .from("coach_athlete_lists")
    .select("id, owner_id, name, list_type, notes, created_at, updated_at")
    .eq("owner_id", ownerId)
    .order("created_at", { ascending: false });
}

export async function createList(ownerId: string, name: string, listType: ListType) {
  return supabase
    .from("coach_athlete_lists")
    .insert({ owner_id: ownerId, name, list_type: listType })
    .select("id, owner_id, name, list_type, notes, created_at, updated_at")
    .single();
}

export async function deleteList(listId: string) {
  return supabase.from("coach_athlete_lists").delete().eq("id", listId);
}

export interface ListMember {
  id: string;
  list_id: string;
  athlete_id: string;
  added_at: string;
}

export async function getListMembers(listId: string) {
  return supabase
    .from("coach_athlete_list_members")
    .select("id, list_id, athlete_id, added_at")
    .eq("list_id", listId)
    .order("added_at", { ascending: false });
}

// RLS requires the target athlete to be currently connected (accepted)
// - see migration 0010. A non-connected athlete_id is rejected server-
// side regardless of what the client sends.
export async function addListMember(listId: string, athleteId: string) {
  return supabase
    .from("coach_athlete_list_members")
    .insert({ list_id: listId, athlete_id: athleteId })
    .select("id, list_id, athlete_id, added_at")
    .single();
}

export async function removeListMember(memberId: string) {
  return supabase.from("coach_athlete_list_members").delete().eq("id", memberId);
}
