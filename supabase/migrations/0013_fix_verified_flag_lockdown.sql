-- Fixes 0011_lock_down_verified_flag.sql, which did not work - confirmed
-- live: a coach's direct self-PATCH to verified=true went through
-- despite that migration.
--
-- Root cause (confirmed via the temporary debug_role_context() function
-- from 0012_diagnose_role_context.sql, called both as the QA coach over
-- REST and directly in the Supabase SQL editor):
--   - Real API call (PostgREST, as the QA coach): current_user =
--     'authenticated', session_user = 'authenticator'.
--   - Supabase SQL editor (the project owner running SQL directly):
--     current_user = 'postgres', session_user = 'postgres'.
-- 0011's trigger function was declared SECURITY DEFINER. Inside a
-- SECURITY DEFINER function, `current_user` reports the FUNCTION
-- OWNER's identity (whoever ran the migration that created it, i.e.
-- 'postgres'), not the real caller's role - this is standard Postgres
-- behavior, not a Postgres bug. So the trigger's `current_user =
-- 'authenticated'` check was comparing 'postgres' to 'authenticated'
-- on every single call, real API request or not, and never matched -
-- the check silently never fired.
--
-- The fix: `session_user` is NOT affected by SECURITY DEFINER (it
-- always reflects the actual connecting session's role, unlike
-- current_user which SECURITY DEFINER and SET ROLE both change) - it
-- correctly reported 'authenticator' for the real API call above
-- regardless of the function's security mode. Switching the check to
-- session_user = 'authenticator' makes it correct AND immune to this
-- entire class of mistake going forward, regardless of whether this or
-- any future version of the function is declared SECURITY DEFINER or
-- not. This version also drops SECURITY DEFINER entirely, since the
-- function never needed elevated privileges to inspect NEW/OLD/TG_OP -
-- it was only added out of misplaced consistency with the discovery
-- functions in 0009, which was the actual source of the bug.
--
-- Also drops the temporary debug_role_context() function from 0012 -
-- its job is done, no reason to leave a role-introspection function
-- sitting in the schema permanently.
--
-- Run this once in the Supabase SQL editor for this project, after
-- 0012_diagnose_role_context.sql.
--
-- Rollback:
--   (restores 0011's original, broken behavior - not recommended)
--   create or replace function public.prevent_self_verification()
--     returns trigger language plpgsql security definer set search_path = public as $$
--     begin
--       if current_user = 'authenticated' then
--         if tg_op = 'INSERT' then new.verified := false;
--         elsif tg_op = 'UPDATE' and new.verified is distinct from old.verified then
--           raise exception 'verified status cannot be changed through the API';
--         end if;
--       end if;
--       return new;
--     end;
--     $$;

drop function if exists public.debug_role_context();

create or replace function public.prevent_self_verification()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  if session_user = 'authenticator' then
    if tg_op = 'INSERT' then
      new.verified := false;
    elsif tg_op = 'UPDATE' and new.verified is distinct from old.verified then
      raise exception 'verified status cannot be changed through the API';
    end if;
  end if;
  return new;
end;
$$;
