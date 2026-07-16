-- Two deliberately separate concepts (per explicit project-owner
-- direction - do not merge these into one generic "shortlist" table):
--
-- 1. coach_athlete_bookmarks - a private, pre-connection SCOUTING
--    bookmark. Created only from a currently-discoverable (adult,
--    opted-in) search result. Grants NO additional visibility beyond
--    what discovery already exposes - it is just a coach_id/athlete_id
--    pointer, no denormalized profile snapshot. Display data is always
--    re-resolved live through get_bookmarked_athlete_cards(), which
--    re-runs the exact same eligibility check on every read - so if the
--    athlete later withdraws discoverability, the bookmark row is kept
--    (an inert, opaque reference - "Option B" from the two choices the
--    project owner offered) but the UI gets nulled-out fields plus
--    `visible = false` and must render "Athlete no longer discoverable,"
--    never stale profile data. This is the mechanism, not a cron job or
--    a delete-on-withdrawal trigger - there is nothing to clean up
--    because nothing sensitive was ever stored on the bookmark row.
--
-- 2. coach_athlete_lists / coach_athlete_list_members - named,
--    purpose-typed ROSTER SELECTION lists ("State Trials 2026"), for
--    athletes already in an accepted connection only. Membership never
--    grants profile/performance access by itself - that remains gated
--    entirely by the pre-existing accepted-connection RLS policies from
--    migration 0005. A list may retain a member after that connection
--    is later revoked (same "outlives the relationship" precedent as
--    coach_athlete_notes, migration 0006) - the list is just a record
--    of "this athlete was selected for X on this date," not a live
--    grant; the coach still can't see that athlete's current profile or
--    performances once revoked, list membership or not.
--
--    owner_id (not coach_id) is deliberate: this table already works
--    identically for a coach or an academy account today (exactly like
--    coach_athlete_connections.coach_id already does per migration
--    0005's own comment), and naming it generically leaves room for a
--    future multi-seat organization model to become owner_id's target
--    without a column rename - there is no such multi-seat/org model in
--    this schema today (academy_profiles is still one profiles.id, one
--    login, same as a coach), so "individual vs. organization
--    ownership" is not a real fork to build for yet, just a naming
--    choice that avoids foreclosing it later.
--
-- Run this once in the Supabase SQL editor for this project, after
-- 0009_add_athlete_discovery.sql.
--
-- Rollback:
--   alter table public.discovery_audit_log drop constraint if exists discovery_audit_log_event_type_check;
--   alter table public.discovery_audit_log add constraint discovery_audit_log_event_type_check check (event_type in ('search', 'connection_request_by_id', 'discoverable_opt_in', 'discoverable_opt_out'));
--   drop policy if exists "Owner can remove members from own lists" on public.coach_athlete_list_members;
--   drop policy if exists "Owner can add currently-connected athletes to own lists" on public.coach_athlete_list_members;
--   drop policy if exists "Owner can view own list members" on public.coach_athlete_list_members;
--   drop table if exists public.coach_athlete_list_members;
--   drop policy if exists "Owner can manage own lists" on public.coach_athlete_lists;
--   drop table if exists public.coach_athlete_lists;
--   drop trigger if exists coach_athlete_bookmarks_audit on public.coach_athlete_bookmarks;
--   drop function if exists public.log_bookmark_change();
--   drop function if exists public.get_bookmarked_athlete_cards();
--   drop policy if exists "Coach can delete own bookmarks" on public.coach_athlete_bookmarks;
--   drop policy if exists "Coach can create bookmarks for currently discoverable athletes" on public.coach_athlete_bookmarks;
--   drop policy if exists "Coach can view own bookmarks" on public.coach_athlete_bookmarks;
--   drop table if exists public.coach_athlete_bookmarks;

-- Widen discovery_audit_log's event_type check (created in
-- 0009_add_athlete_discovery.sql with an explicit constraint name for
-- exactly this reason) to also allow the two bookmark events logged by
-- the trigger below.
alter table public.discovery_audit_log drop constraint discovery_audit_log_event_type_check;
alter table public.discovery_audit_log add constraint discovery_audit_log_event_type_check
  check (event_type in (
    'search',
    'connection_request_by_id',
    'discoverable_opt_in',
    'discoverable_opt_out',
    'bookmark_created',
    'bookmark_removed'
  ));

create table public.coach_athlete_bookmarks (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid not null references public.profiles(id) on delete cascade,
  athlete_id uuid not null references public.athlete_profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  unique (coach_id, athlete_id)
);

create index coach_athlete_bookmarks_coach_id_idx on public.coach_athlete_bookmarks (coach_id);

alter table public.coach_athlete_bookmarks enable row level security;

create policy "Coach can view own bookmarks"
  on public.coach_athlete_bookmarks
  for select
  using (auth.uid() = coach_id);

-- Both the caller's entitlement AND the target's live eligibility are
-- required here, not just one. Checking only target eligibility would
-- let an UNVERIFIED coach who guesses (or is otherwise handed) a real
-- discoverable adult's athlete_id bookmark them anyway - a guessed-ID
-- bypass of the verification requirement. Checking only entitlement
-- would let a verified coach bookmark a non-discoverable/underage
-- athlete_id. Both together close both holes at once.
create policy "Coach can create bookmarks for currently discoverable athletes"
  on public.coach_athlete_bookmarks
  for insert
  with check (
    auth.uid() = coach_id
    and public.caller_has_discovery_entitlement()
    and public.is_athlete_currently_discoverable(athlete_id)
  );

create policy "Coach can delete own bookmarks"
  on public.coach_athlete_bookmarks
  for delete
  using (auth.uid() = coach_id);

-- The only supported read path for bookmark display data - never join
-- coach_athlete_bookmarks straight to profiles/athlete_profiles from
-- the client. `visible` is true if EITHER the athlete is still
-- currently discoverable OR the coach has since formed an accepted
-- connection with them (a later real connection is a strictly stronger,
-- independent basis for visibility, not something discovery withdrawal
-- should regress) - false otherwise, in which case every display field
-- is nulled rather than left stale.
create or replace function public.get_bookmarked_athlete_cards()
returns table (
  bookmark_id uuid,
  athlete_id uuid,
  full_name text,
  preferred_event text,
  secondary_event text,
  state text,
  visible boolean
)
language sql
stable
security definer
set search_path = public
as $$
  select
    b.id,
    b.athlete_id,
    case when v.is_visible then p.full_name else null end,
    case when v.is_visible then ap.preferred_event else null end,
    case when v.is_visible then ap.secondary_event else null end,
    case when v.is_visible then p.state else null end,
    v.is_visible
  from public.coach_athlete_bookmarks b
  join public.profiles p on p.id = b.athlete_id
  join public.athlete_profiles ap on ap.id = b.athlete_id
  cross join lateral (
    select
      public.is_athlete_currently_discoverable(b.athlete_id)
      or exists (
        select 1 from public.coach_athlete_connections c
        where c.coach_id = b.coach_id
          and c.athlete_id = b.athlete_id
          and c.status = 'accepted'
      ) as is_visible
  ) v
  where b.coach_id = auth.uid();
$$;

revoke all on function public.get_bookmarked_athlete_cards() from public, anon;
grant execute on function public.get_bookmarked_athlete_cards() to authenticated;

create or replace function public.log_bookmark_change()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if tg_op = 'INSERT' then
    insert into public.discovery_audit_log (actor_id, event_type, target_athlete_id)
    values (new.coach_id, 'bookmark_created', new.athlete_id);
    return new;
  elsif tg_op = 'DELETE' then
    insert into public.discovery_audit_log (actor_id, event_type, target_athlete_id)
    values (old.coach_id, 'bookmark_removed', old.athlete_id);
    return old;
  end if;
  return null;
end;
$$;

create trigger coach_athlete_bookmarks_audit
  after insert or delete on public.coach_athlete_bookmarks
  for each row execute function public.log_bookmark_change();

-- Roster selection lists - see the top-of-file comment for why these
-- are a fully separate concept from bookmarks above.
create table public.coach_athlete_lists (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references public.profiles(id) on delete cascade,
  name text not null,
  list_type text not null check (list_type in (
    'TOURNAMENT_SELECTION', 'CAMP_SELECTION', 'TRIAL_SELECTION', 'TEAM_SQUAD'
  )),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index coach_athlete_lists_owner_id_idx on public.coach_athlete_lists (owner_id);

alter table public.coach_athlete_lists enable row level security;

create policy "Owner can manage own lists"
  on public.coach_athlete_lists
  for all
  using (auth.uid() = owner_id)
  with check (auth.uid() = owner_id);

create table public.coach_athlete_list_members (
  id uuid primary key default gen_random_uuid(),
  list_id uuid not null references public.coach_athlete_lists(id) on delete cascade,
  athlete_id uuid not null references public.athlete_profiles(id) on delete cascade,
  added_at timestamptz not null default now(),
  unique (list_id, athlete_id)
);

create index coach_athlete_list_members_list_id_idx on public.coach_athlete_list_members (list_id);

alter table public.coach_athlete_list_members enable row level security;

create policy "Owner can view own list members"
  on public.coach_athlete_list_members
  for select
  using (
    exists (
      select 1 from public.coach_athlete_lists l
      where l.id = list_id and l.owner_id = auth.uid()
    )
  );

-- Members must be connected AT INSERT TIME - checked here, not
-- re-checked later. A subsequent revocation does not retroactively
-- remove the row (matches the notes precedent) but also grants nothing
-- extra: actual profile/performance access is independently re-checked
-- live by the accepted-connection policies on every read, list
-- membership or not.
create policy "Owner can add currently-connected athletes to own lists"
  on public.coach_athlete_list_members
  for insert
  with check (
    exists (
      select 1 from public.coach_athlete_lists l
      where l.id = list_id and l.owner_id = auth.uid()
    )
    and exists (
      select 1 from public.coach_athlete_connections c
      where c.coach_id = auth.uid()
        and c.athlete_id = coach_athlete_list_members.athlete_id
        and c.status = 'accepted'
    )
  );

create policy "Owner can remove members from own lists"
  on public.coach_athlete_list_members
  for delete
  using (
    exists (
      select 1 from public.coach_athlete_lists l
      where l.id = list_id and l.owner_id = auth.uid()
    )
  );
