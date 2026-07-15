-- Coach/academy <-> athlete connection requests. Neither side has any
-- visibility into the other's data until a request is explicitly
-- accepted (or, for basic name/org info, while a request they *received*
-- is still pending - see the profiles/coach_profiles/academy_profiles
-- policies below, which are deliberately directional, not symmetric).
--
-- coach_id holds a coach OR academy account's profiles.id - both roles
-- share this table for Phase 1 rather than inventing two parallel
-- tables. partner_role records which one, denormalized at insert time,
-- so "all connections for this academy" is queryable without a join to
-- profiles and without needing an organizations table yet.
--
-- Run this once in the Supabase SQL editor for this project.
--
-- Rollback:
--   drop policy if exists "Coach can view accepted athlete performances" on public.performances;
--   drop policy if exists "Coach can view accepted athlete profile" on public.athlete_profiles;
--   drop policy if exists "Connected/requesting athletes can view academy profile" on public.academy_profiles;
--   drop policy if exists "Connected/requesting athletes can view coach profile" on public.coach_profiles;
--   drop policy if exists "Connection parties can view relevant profiles" on public.profiles;
--   drop function if exists public.request_partner_connection(text);
--   drop trigger if exists coach_athlete_connections_transition on public.coach_athlete_connections;
--   drop function if exists public.enforce_coach_athlete_connection_transition();
--   drop table if exists public.coach_athlete_connections;

create table public.coach_athlete_connections (
  id uuid primary key default gen_random_uuid(),
  coach_id uuid not null references public.profiles(id) on delete cascade,
  athlete_id uuid not null references public.athlete_profiles(id) on delete cascade,
  partner_role text not null check (partner_role in ('coach', 'academy')),
  status text not null default 'pending' check (status in ('pending', 'accepted', 'rejected', 'revoked')),
  initiated_by text not null check (initiated_by in ('coach', 'athlete')),
  -- Echoes the email the initiator typed into request_partner_connection().
  -- Not a new information disclosure: the initiator already knows this
  -- email (they typed it), and the recipient seeing their own email back
  -- is not a leak either. Exists purely so the initiator's own "sent
  -- invitations" list can show who they invited before the recipient
  -- profile itself becomes visible to them (see the directional policies
  -- below - the initiator has no other way to see that until acceptance).
  invited_email text,
  requested_at timestamptz not null default now(),
  responded_at timestamptz,
  created_at timestamptz not null default now(),
  unique (coach_id, athlete_id)
);

create index coach_athlete_connections_athlete_id_idx
  on public.coach_athlete_connections (athlete_id);

alter table public.coach_athlete_connections enable row level security;

-- Row-visibility only. All transition legality (who may move a row from
-- pending -> accepted/rejected, accepted -> revoked, or reactivate a
-- rejected/revoked row) lives in the trigger below, not in RLS. A prior
-- draft of this migration used two separate UPDATE policies (one for
-- "respond", one for "revoke") - that's a known Postgres RLS trap:
-- multiple permissive policies for the same command combine their
-- USING clauses with OR and their WITH CHECK clauses with OR
-- *independently*, not as matched pairs. That let a recipient of a
-- still-pending request jump straight to "revoked" by satisfying one
-- policy's USING and a different policy's WITH CHECK. Collapsing to one
-- broad access policy plus a trigger that owns the whole state machine
-- avoids that class of bug entirely.
create policy "Parties can view their own connections"
  on public.coach_athlete_connections
  for select
  using (auth.uid() = coach_id or auth.uid() = athlete_id);

create policy "Parties can update their own connections"
  on public.coach_athlete_connections
  for update
  using (auth.uid() = coach_id or auth.uid() = athlete_id)
  with check (auth.uid() = coach_id or auth.uid() = athlete_id);

-- Deliberately no INSERT policy. Creation only happens through
-- request_partner_connection() below (SECURITY DEFINER), which is the
-- only way to resolve "who does this email belong to" without first
-- granting broad SELECT on profiles by email to any authenticated user.

create or replace function public.enforce_coach_athlete_connection_transition()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.coach_id <> old.coach_id or new.athlete_id <> old.athlete_id then
    raise exception 'coach_id/athlete_id cannot be changed';
  end if;

  -- initiated_by may only change as part of a legitimate reactivation
  -- (see the reactivation branch below), never on any other update.
  if new.initiated_by <> old.initiated_by
     and not (old.status in ('rejected', 'revoked') and new.status = 'pending') then
    raise exception 'initiated_by cannot be changed outside of reactivation';
  end if;

  if old.status = 'pending' and new.status in ('accepted', 'rejected') then
    if old.initiated_by = 'coach' and auth.uid() <> old.athlete_id then
      raise exception 'only the invited athlete may respond to this request';
    elsif old.initiated_by = 'athlete' and auth.uid() <> old.coach_id then
      raise exception 'only the invited coach/academy may respond to this request';
    end if;
    new.responded_at := now();

  elsif old.status = 'accepted' and new.status = 'revoked' then
    if auth.uid() <> old.coach_id and auth.uid() <> old.athlete_id then
      raise exception 'only a party to this connection may revoke it';
    end if;
    new.responded_at := now();

  elsif old.status in ('rejected', 'revoked') and new.status = 'pending' then
    -- Reactivation is only reachable through request_partner_connection(),
    -- which sets this transaction-local flag right before its own
    -- ON CONFLICT ... DO UPDATE. A raw client UPDATE attempting the same
    -- transition (bypassing the RPC's email/role validation entirely)
    -- is rejected here.
    if coalesce(current_setting('app.connection_reactivation', true), 'false') <> 'true' then
      raise exception 'reactivating a connection requires request_partner_connection()';
    end if;
    new.requested_at := now();
    new.responded_at := null;

  else
    raise exception 'invalid status transition from % to %', old.status, new.status;
  end if;

  return new;
end;
$$;

create trigger coach_athlete_connections_transition
  before update on public.coach_athlete_connections
  for each row execute function public.enforce_coach_athlete_connection_transition();

-- Resolves "which account does this email belong to" server-side so the
-- inviting party never needs direct SELECT access to a stranger's
-- profiles row. Returns only the new connection's id - never the target
-- profile's data - and every failure path (no such account, wrong role
-- pairing, already connected/pending, or any unexpected error) raises
-- the identical generic message, so this can't be used to distinguish
-- "no such email" from "that email belongs to the wrong role" from
-- "already connected". Not rate-limited (nothing in this app is - see
-- docs/ENGINEERING_HANDOFF.md #11) - a known, flagged gap, not solved here.
create or replace function public.request_partner_connection(target_email text)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  caller_id uuid := auth.uid();
  caller_role text;
  target_id uuid;
  target_role text;
  conn_id uuid;
begin
  if caller_id is null then
    raise exception 'connection request could not be created';
  end if;

  select role into caller_role from public.profiles where id = caller_id;
  select id, role into target_id, target_role from public.profiles where email = target_email;

  if target_id is null then
    raise exception 'connection request could not be created';
  end if;

  perform set_config('app.connection_reactivation', 'true', true);

  if caller_role in ('coach', 'academy') and target_role = 'athlete' then
    insert into public.coach_athlete_connections
      (coach_id, athlete_id, partner_role, initiated_by, status, invited_email)
    values (caller_id, target_id, caller_role, 'coach', 'pending', target_email)
    on conflict (coach_id, athlete_id) do update
      set status = 'pending', initiated_by = 'coach', requested_at = now(),
          responded_at = null, invited_email = target_email
      where public.coach_athlete_connections.status in ('rejected', 'revoked')
    returning id into conn_id;

  elsif caller_role = 'athlete' and target_role in ('coach', 'academy') then
    insert into public.coach_athlete_connections
      (coach_id, athlete_id, partner_role, initiated_by, status, invited_email)
    values (target_id, caller_id, target_role, 'athlete', 'pending', target_email)
    on conflict (coach_id, athlete_id) do update
      set status = 'pending', initiated_by = 'athlete', requested_at = now(),
          responded_at = null, invited_email = target_email
      where public.coach_athlete_connections.status in ('rejected', 'revoked')
    returning id into conn_id;

  else
    conn_id := null;
  end if;

  if conn_id is null then
    raise exception 'connection request could not be created';
  end if;

  return conn_id;
exception
  when others then
    raise exception 'connection request could not be created';
end;
$$;

revoke all on function public.request_partner_connection(text) from public, anon;
grant execute on function public.request_partner_connection(text) to authenticated;

-- Additive cross-table visibility, gated by connection state. Nothing
-- below touches or weakens any existing policy.

-- Directional, not symmetric: only the *recipient* of a still-pending
-- request can see the initiator's base profile (name/email/role) - not
-- the other way around. A symmetric version was the first draft here;
-- it was rejected because it turned request_partner_connection()'s
-- generic-exception design into a two-step oracle (call the RPC to
-- confirm an email is a registered athlete, then read their real name
-- straight back off the now-visible pending row).
create policy "Connection parties can view relevant profiles"
  on public.profiles
  for select
  using (
    exists (
      select 1 from public.coach_athlete_connections c
      where (
        (c.coach_id = profiles.id and c.athlete_id = auth.uid())
        or (c.athlete_id = profiles.id and c.coach_id = auth.uid())
      )
      and (
        c.status = 'accepted'
        or (
          c.status = 'pending'
          and (
            (c.initiated_by = 'coach' and auth.uid() = c.athlete_id)
            or (c.initiated_by = 'athlete' and auth.uid() = c.coach_id)
          )
        )
      )
    )
  );

create policy "Connected/requesting athletes can view coach profile"
  on public.coach_profiles
  for select
  using (
    exists (
      select 1 from public.coach_athlete_connections c
      where c.coach_id = coach_profiles.id
        and c.athlete_id = auth.uid()
        and (c.status = 'accepted' or (c.status = 'pending' and c.initiated_by = 'coach'))
    )
  );

create policy "Connected/requesting athletes can view academy profile"
  on public.academy_profiles
  for select
  using (
    exists (
      select 1 from public.coach_athlete_connections c
      where c.coach_id = academy_profiles.id
        and c.athlete_id = auth.uid()
        and (c.status = 'accepted' or (c.status = 'pending' and c.initiated_by = 'coach'))
    )
  );

-- Full athlete data (DOB, height/weight, performances, analysis
-- results) only unlocks on acceptance - never at pending.
create policy "Coach can view accepted athlete profile"
  on public.athlete_profiles
  for select
  using (
    exists (
      select 1 from public.coach_athlete_connections c
      where c.athlete_id = athlete_profiles.id
        and c.coach_id = auth.uid()
        and c.status = 'accepted'
    )
  );

create policy "Coach can view accepted athlete performances"
  on public.performances
  for select
  using (
    exists (
      select 1 from public.coach_athlete_connections c
      where c.athlete_id = performances.athlete_id
        and c.coach_id = auth.uid()
        and c.status = 'accepted'
    )
  );
