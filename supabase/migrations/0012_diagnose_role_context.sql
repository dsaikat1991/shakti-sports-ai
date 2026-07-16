-- TEMPORARY diagnostic only - not a real feature. 0011's trigger
-- checked `current_user = 'authenticated'`, but that check silently
-- never fired (the coach's self-PATCH to verified=true went through
-- anyway, confirmed live). Root cause hypothesis: 0011's trigger
-- function is SECURITY DEFINER, and inside a SECURITY DEFINER function,
-- `current_user` reflects the FUNCTION OWNER's identity (whoever ran
-- the migration), not the original caller's role - that's standard
-- Postgres semantics, not a bug in Postgres, but it means the trigger
-- was checking the wrong thing.
--
-- This function is SECURITY INVOKER (the default - no `security
-- definer` line) specifically so it reports the real, unaffected
-- values, to confirm the hypothesis before shipping a real fix.
--
-- Rollback:
--   drop function if exists public.debug_role_context();
create or replace function public.debug_role_context()
returns table (current_user_name text, session_user_name text, role_setting text)
language sql
stable
as $$
  select current_user::text, session_user::text, current_setting('role', true);
$$;

grant execute on function public.debug_role_context() to authenticated;
