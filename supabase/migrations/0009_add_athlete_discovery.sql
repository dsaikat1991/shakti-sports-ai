-- Talent discovery (Coach/Academy Console Phase 2). Lets a VERIFIED
-- coach/academy account search for adult, opted-in athletes without an
-- existing connection, and send a connection request directly from a
-- search result. Everything else in this schema (accepted-connection
-- gated profile/performance access, private notes) is untouched.
--
-- Five hard requirements shaped this design, all specified by the
-- project owner before this was written - see docs/ENGINEERING_HANDOFF.md
-- for the full reasoning:
--
-- 1. Discovery is NOT unlocked by self-declared role. It requires
--    coach_profiles.verified / academy_profiles.verified = true (the
--    verification tier that already existed, unused, since migration
--    0005/§18.2 - this is the "smallest safe foundation" reuse of it,
--    not a new column). No verification workflow exists yet, so these
--    flags are set manually by the project owner (Supabase dashboard/
--    SQL editor) until a real verification workflow is built - every
--    existing coach/academy account is UNVERIFIED by default and gets
--    ZERO discovery access until then. This is intentional, not a bug.
-- 2. A boolean discoverable flag alone is not sufficient for minors.
--    Eligibility is COMPUTED (public.is_athlete_currently_discoverable),
--    not just read from the column: discoverable = true AND a
--    date_of_birth on file implying age >= 18. No guardian-consent
--    system exists in this schema, so minors are unconditionally
--    excluded from discovery in this phase - not "excluded unless a
--    guardian later approves," just excluded, full stop, until that
--    infrastructure exists. A athlete with no date_of_birth on file is
--    also excluded (conservative default - never assume adult).
-- 3. The returned field set is deliberately minimal: athlete_id,
--    full_name, preferred_event, secondary_event, state. NOT returned:
--    date_of_birth/age, academy (private academy/school info), district
--    (more precise than state, no separate permission model exists to
--    unlock it), contact info, guardian info, or any performance/
--    biomechanics data. The RPC's RETURNS TABLE is an explicit column
--    list - it can never leak athlete_profiles.* by construction.
-- 4. Every SECURITY DEFINER function here: has a fixed `set search_path
--    = public`, schema-qualifies every reference, explicitly rejects
--    auth.uid() is null, checks entitlement/eligibility inside the
--    function body (never trusts a prior frontend call), uses no
--    dynamic SQL, and has EXECUTE revoked from public/anon and granted
--    only to `authenticated`.
-- 5. Search is paginated (server-clamped to a max page size), requires
--    at least one real filter (no "dump every discoverable athlete"
--    call), and never returns a total count.
--
-- Also added: discovery_audit_log - write-only from the SECURITY
-- DEFINER functions/triggers below, no SELECT policy for ordinary
-- users (same pattern as contact_submissions, §17.3) - covers search
-- calls, connection requests raised via discovery, and discoverable
-- opt-in/opt-out events, for later abuse review by the project owner.
-- Rate limiting itself is NOT implemented here (nothing in this app is
-- rate-limited anywhere yet, see §11/§17.7) - flagged as a production
-- requirement before real nationwide discovery is declared ready, not
-- solved by this migration.
--
-- Run this once in the Supabase SQL editor for this project, after
-- 0008_add_avatars_bucket.sql.
--
-- Rollback:
--   drop trigger if exists athlete_profiles_discoverable_audit on public.athlete_profiles;
--   drop function if exists public.log_discoverable_change();
--   drop function if exists public.request_partner_connection_by_athlete_id(uuid);
--   drop function if exists public.search_discoverable_athletes(text, text, int, int);
--   drop function if exists public.caller_has_discovery_entitlement();
--   drop function if exists public.is_athlete_currently_discoverable(uuid);
--   drop table if exists public.discovery_audit_log;
--   alter table public.athlete_profiles drop column if exists discoverable;

alter table public.athlete_profiles add column discoverable boolean not null default false;

-- Write-only audit trail. No SELECT policy for `authenticated` - only
-- readable via the Supabase dashboard/SQL editor (project owner only).
-- No INSERT policy either - every row is written by a SECURITY DEFINER
-- function/trigger below, which bypasses RLS entirely, so an ordinary
-- client can never write (or forge) an audit entry directly.
create table public.discovery_audit_log (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references public.profiles(id) on delete set null,
  -- Named explicitly (not left to Postgres's auto-generated name) so
  -- 0010_add_coach_athlete_bookmarks_and_lists.sql can safely widen this
  -- constraint to add its own event types without guessing a name.
  event_type text not null,
  target_athlete_id uuid references public.athlete_profiles(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table public.discovery_audit_log
  add constraint discovery_audit_log_event_type_check
  check (event_type in (
    'search',
    'connection_request_by_id',
    'discoverable_opt_in',
    'discoverable_opt_out'
  ));

create index discovery_audit_log_actor_id_idx on public.discovery_audit_log (actor_id);
create index discovery_audit_log_created_at_idx on public.discovery_audit_log (created_at);

alter table public.discovery_audit_log enable row level security;

-- Single source of truth for "is this athlete visible to discovery right
-- now" - reused by the search RPC, the connect-by-id RPC, and (in
-- 0010_add_coach_athlete_bookmarks_and_lists.sql) bookmark creation and
-- resolution. Centralizing this in one function is deliberate - this
-- codebase has previously shipped bugs from the same eligibility check
-- being hand-copied into multiple places and drifting apart (see
-- docs/ENGINEERING_HANDOFF.md bug #5, landmark_is_usable()).
create or replace function public.is_athlete_currently_discoverable(target_athlete_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.athlete_profiles ap
    where ap.id = target_athlete_id
      and ap.discoverable = true
      and ap.date_of_birth is not null
      and ap.date_of_birth <= (current_date - interval '18 years')
  );
$$;

revoke all on function public.is_athlete_currently_discoverable(uuid) from public, anon;
grant execute on function public.is_athlete_currently_discoverable(uuid) to authenticated;

-- The verification-tier gate (requirement #1). Reuses coach_profiles.
-- verified / academy_profiles.verified - both already existed, unused,
-- specifically flagged in §18.2 as "the future verification tier" for
-- this exact purpose. No new column.
create or replace function public.caller_has_discovery_entitlement()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.profiles p
    left join public.coach_profiles cp on cp.id = p.id
    left join public.academy_profiles acp on acp.id = p.id
    where p.id = auth.uid()
      and (
        (p.role = 'coach' and cp.verified = true)
        or (p.role = 'academy' and acp.verified = true)
      )
  );
$$;

revoke all on function public.caller_has_discovery_entitlement() from public, anon;
grant execute on function public.caller_has_discovery_entitlement() to authenticated;

-- Returns ONLY the approved column set (requirement #3) - never
-- athlete_profiles.* or profiles.*. An unentitled caller (wrong role,
-- or right role but not verified) gets an empty result set, identical
-- in shape to "verified but no matches" - no oracle for entitlement
-- status. Requires at least one real filter (requirement #5) - this is
-- checked AFTER the entitlement check, so an unentitled caller never
-- even reaches the filter-validation branch, keeping their observed
-- behavior uniform regardless of what they pass in.
create or replace function public.search_discoverable_athletes(
  p_event text default null,
  p_state text default null,
  p_limit int default 20,
  p_offset int default 0
)
returns table (
  athlete_id uuid,
  full_name text,
  preferred_event text,
  secondary_event text,
  state text
)
language plpgsql
volatile
security definer
set search_path = public
as $$
declare
  safe_limit int := least(greatest(coalesce(p_limit, 20), 1), 20);
  safe_offset int := greatest(coalesce(p_offset, 0), 0);
  is_entitled boolean;
begin
  if auth.uid() is null then
    raise exception 'authentication required';
  end if;

  -- Validated BEFORE the audit-log insert below, deliberately. A `raise
  -- exception` aborts the whole call, including any insert already done
  -- earlier in it - so any exception raised after the audit insert would
  -- silently roll that log entry back too. Putting every remaining
  -- exception-raising check first means any call that reaches the audit
  -- insert is guaranteed to complete (either an empty return or a real
  -- query) with no further raise, so the log entry always durably lands.
  if p_event is null and p_state is null then
    raise exception 'at least one search filter is required';
  end if;

  is_entitled := public.caller_has_discovery_entitlement();

  insert into public.discovery_audit_log (actor_id, event_type, metadata)
  values (
    auth.uid(),
    'search',
    jsonb_build_object(
      'authorized', is_entitled,
      'event', p_event,
      'state', p_state
    )
  );

  if not is_entitled then
    return; -- empty result set, not an error - see comment above
  end if;

  return query
    select p.id, p.full_name, ap.preferred_event, ap.secondary_event, p.state
    from public.profiles p
    join public.athlete_profiles ap on ap.id = p.id
    where ap.discoverable = true
      and ap.date_of_birth is not null
      and ap.date_of_birth <= (current_date - interval '18 years')
      and (p_event is null or ap.preferred_event = p_event or ap.secondary_event = p_event)
      and (p_state is null or p.state = p_state)
    order by p.id
    limit safe_limit
    offset safe_offset;
end;
$$;

revoke all on function public.search_discoverable_athletes(text, text, int, int) from public, anon;
grant execute on function public.search_discoverable_athletes(text, text, int, int) to authenticated;

-- Lets a coach/academy send a connection request straight from a search
-- result, without ever being shown the athlete's email (unlike the
-- existing email-based request_partner_connection, which is fine there
-- because the inviter already typed the email themselves). This
-- function independently re-verifies BOTH caller entitlement and target
-- eligibility at call time (requirement #4) - it never trusts that the
-- athlete legitimately appeared in an earlier search response, which
-- closes a guessed-UUID bypass (an unverified coach, or a verified one
-- targeting a since-withdrawn/underage athlete, gets rejected here even
-- if they somehow obtained a real athlete_id).
--
-- Deliberately does NOT populate invited_email (unlike the email-based
-- RPC) - the coach never provided an email, and this SECURITY DEFINER
-- function bypassing RLS to fetch one and hand it back would recreate
-- exactly the email-disclosure the discovery result set was designed to
-- avoid. The frontend's "sent invitations" list must show a generic
-- label for a null-invited_email, coach-initiated, pending row rather
-- than expecting to redisplay a name/email it isn't entitled to re-read
-- (the directional pending-visibility policy from migration 0005
-- correctly blocks the coach, as initiator, from re-reading the
-- target's profile - see docs/ENGINEERING_HANDOFF.md for why this
-- direction is intentional, not a UX bug to work around here).
--
-- Preserves every existing protection from request_partner_connection:
-- the same ON CONFLICT ... DO UPDATE ... WHERE status IN (rejected,
-- revoked) means a duplicate request against an already pending/
-- accepted connection silently no-ops (conn_id stays null, generic
-- exception raised) - not overwritable. Self-request is explicitly
-- blocked too, though it is already structurally impossible (a coach
-- and an athlete are always different profiles.id values). No block/
-- suspension system exists anywhere in this schema yet, so there is
-- nothing of that kind to preserve here - noted, not fabricated.
--
-- The audit-log insert happens after every entitlement/eligibility
-- check but before the actual connection insert - so an unauthorized or
-- ineligible attempt is always durably logged (nothing raises after
-- that point until the connection insert itself). A subsequent
-- duplicate-request rollback (conn_id ends up null) does roll back this
-- specific log entry too, same rollback-eats-the-log caveat as above -
-- accepted here since that case isn't the abuse signal being monitored
-- for; the security-relevant checks are what's guaranteed logged.
create or replace function public.request_partner_connection_by_athlete_id(target_athlete_id uuid)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  caller_id uuid := auth.uid();
  caller_role text;
  conn_id uuid;
begin
  if caller_id is null then
    raise exception 'connection request could not be created';
  end if;

  if target_athlete_id = caller_id then
    raise exception 'connection request could not be created';
  end if;

  if not public.caller_has_discovery_entitlement() then
    raise exception 'connection request could not be created';
  end if;

  if not public.is_athlete_currently_discoverable(target_athlete_id) then
    raise exception 'connection request could not be created';
  end if;

  select role into caller_role from public.profiles where id = caller_id;

  insert into public.discovery_audit_log (actor_id, event_type, target_athlete_id)
  values (caller_id, 'connection_request_by_id', target_athlete_id);

  perform set_config('app.connection_reactivation', 'true', true);

  insert into public.coach_athlete_connections
    (coach_id, athlete_id, partner_role, initiated_by, status, invited_email)
  values (caller_id, target_athlete_id, caller_role, 'coach', 'pending', null)
  on conflict (coach_id, athlete_id) do update
    set status = 'pending', initiated_by = 'coach', requested_at = now(),
        responded_at = null, invited_email = null
    where public.coach_athlete_connections.status in ('rejected', 'revoked')
  returning id into conn_id;

  if conn_id is null then
    raise exception 'connection request could not be created';
  end if;

  return conn_id;
exception
  when others then
    raise exception 'connection request could not be created';
end;
$$;

revoke all on function public.request_partner_connection_by_athlete_id(uuid) from public, anon;
grant execute on function public.request_partner_connection_by_athlete_id(uuid) to authenticated;

-- Audits every discoverable-flag flip (opt-in and opt-out), regardless
-- of who/what changed it. Discoverability withdrawal is effective
-- immediately by construction - is_athlete_currently_discoverable()
-- reads the live column value on every call, so the very next search/
-- connect/bookmark-resolution call after an opt-out already excludes
-- this athlete. No caching, no batch job, no delay.
create or replace function public.log_discoverable_change()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.discoverable is distinct from old.discoverable then
    insert into public.discovery_audit_log (actor_id, event_type, target_athlete_id)
    values (
      new.id,
      case when new.discoverable then 'discoverable_opt_in' else 'discoverable_opt_out' end,
      new.id
    );
  end if;
  return new;
end;
$$;

create trigger athlete_profiles_discoverable_audit
  after update on public.athlete_profiles
  for each row execute function public.log_discoverable_change();
