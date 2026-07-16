-- Closes a gap discovered while reviewing 0009_add_athlete_discovery.sql
-- after it was applied: coach_profiles.verified / academy_profiles.
-- verified have always used the same owner-only RLS pattern as every
-- other self-editable column on those tables (auth.uid() = id, no
-- column-level restriction - RLS governs rows, not columns). That was
-- harmless while `verified` sat unused (§18.2). It stopped being
-- harmless the moment 0009 started gating discovery on it - as things
-- stood after 0009/0010 alone, any coach could self-PATCH their own row
-- to `verified: true` via a direct REST call and grant themselves
-- nationwide discovery access, fully defeating requirement #1 ("do not
-- grant discovery access merely because a user selected the coach/
-- academy role"). 0009/0010 themselves are not wrong - they just built
-- correctly-gated logic on top of a column that wasn't yet protected
-- for this new, more sensitive purpose. This migration is the fix.
--
-- Approach: a BEFORE INSERT OR UPDATE trigger on both tables that
-- neutralizes any client-supplied `verified` value when the acting
-- Postgres role is `authenticated` - i.e. any request that came through
-- Supabase's normal REST/PostgREST API path, which is how every real
-- end-user session reaches the database. On INSERT (onboarding, when a
-- coach/academy's row is first created) it is silently forced to
-- false - onboarding never intends to set it anyway, this is just a
-- server-side floor. On UPDATE it is hard-rejected with an exception,
-- since no legitimate client flow ever needs to change it. The Supabase
-- SQL editor (how the project owner runs every migration and manual
-- admin action in this repo's established workflow) connects as a
-- different role (`postgres`/the project's own admin connection), not
-- `authenticated`, so it is unaffected - the project owner can still
-- flip `verified` by hand exactly as before. This is the "smallest safe
-- foundation" fix: it does not attempt to build a verification
-- workflow/UI, only closes the self-service bypass on both the create
-- and update paths, matching the same phasing principle already
-- applied to discovery itself.
--
-- Also worth documenting explicitly, not fixed here (a different class
-- of problem - not an authorization bypass, a self-attestation limit):
-- `athlete_profiles.date_of_birth` is self-reported and self-editable,
-- same as it has always been for onboarding/profile edits. An athlete
-- who is actually a minor could misrepresent their DOB to appear 18+
-- and pass the discovery age gate. There is no identity/age-verification
-- integration in this platform to prevent that, and building one is
-- well beyond "smallest safe foundation" for this phase - this is a
-- real, standing residual limitation of self-reported DOB, not
-- something a trigger or RLS policy can close. Flagged here so it isn't
-- mistaken for solved.
--
-- Run this once in the Supabase SQL editor for this project, after
-- 0010_add_coach_athlete_bookmarks_and_lists.sql.
--
-- Rollback:
--   drop trigger if exists academy_profiles_prevent_self_verification on public.academy_profiles;
--   drop trigger if exists coach_profiles_prevent_self_verification on public.coach_profiles;
--   drop function if exists public.prevent_self_verification();

create or replace function public.prevent_self_verification()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if current_user = 'authenticated' then
    if tg_op = 'INSERT' then
      new.verified := false;
    elsif tg_op = 'UPDATE' and new.verified is distinct from old.verified then
      raise exception 'verified status cannot be changed through the API';
    end if;
  end if;
  return new;
end;
$$;

create trigger coach_profiles_prevent_self_verification
  before insert or update on public.coach_profiles
  for each row execute function public.prevent_self_verification();

create trigger academy_profiles_prevent_self_verification
  before insert or update on public.academy_profiles
  for each row execute function public.prevent_self_verification();
