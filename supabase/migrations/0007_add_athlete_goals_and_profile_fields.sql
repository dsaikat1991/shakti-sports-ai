-- Athlete Console completion (see docs/ENGINEERING_HANDOFF.md for the
-- session this belongs to). Two purely additive pieces:
--
-- 1. athlete_goals - backs the Goals module (current goal, description,
--    target date, status). Same owner-only RLS pattern as every other
--    athlete-owned table in this schema (auth.uid() = athlete_id).
-- 2. Three new athlete_profiles columns that had no home before:
--    ai_training_consent (a real, functional Settings toggle - tracked
--    separately from any other consent, matching the same never-bundle
--    principle already used for the coach-console and dataset work),
--    achievements (freeform, same pattern as the existing bio column),
--    deletion_requested_at (backs a "request account deletion" flow -
--    records intent for manual follow-up, does not itself delete
--    anything - no backend cascade-delete endpoint exists yet).
--
-- Run this once in the Supabase SQL editor for this project.
--
-- Rollback:
--   alter table public.athlete_profiles drop column if exists deletion_requested_at;
--   alter table public.athlete_profiles drop column if exists achievements;
--   alter table public.athlete_profiles drop column if exists ai_training_consent;
--   drop table if exists public.athlete_goals;

create table public.athlete_goals (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references public.athlete_profiles(id) on delete cascade,
  description text not null,
  target_date date,
  status text not null default 'active' check (status in ('active', 'completed', 'abandoned')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index athlete_goals_athlete_id_idx on public.athlete_goals (athlete_id);

alter table public.athlete_goals enable row level security;

create policy "Athletes can view own goals"
  on public.athlete_goals
  for select
  using (auth.uid() = athlete_id);

create policy "Athletes can insert own goals"
  on public.athlete_goals
  for insert
  with check (auth.uid() = athlete_id);

create policy "Athletes can update own goals"
  on public.athlete_goals
  for update
  using (auth.uid() = athlete_id)
  with check (auth.uid() = athlete_id);

create policy "Athletes can delete own goals"
  on public.athlete_goals
  for delete
  using (auth.uid() = athlete_id);

alter table public.athlete_profiles add column ai_training_consent boolean not null default false;
alter table public.athlete_profiles add column achievements text;
alter table public.athlete_profiles add column deletion_requested_at timestamptz;
