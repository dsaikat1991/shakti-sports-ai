-- Private per-athlete notes, visible only to the authoring coach/academy
-- account - never the athlete. Kept visible/deletable by the author even
-- after a connection is revoked (it's the coach's own authored content,
-- not the athlete's data); creating or editing a note requires the
-- connection to currently be accepted.
--
-- Run this once in the Supabase SQL editor for this project, after
-- 0005_add_coach_athlete_connections.sql.
--
-- Rollback:
--   drop table if exists public.coach_athlete_notes;

create table public.coach_athlete_notes (
  id uuid primary key default gen_random_uuid(),
  connection_id uuid not null references public.coach_athlete_connections(id) on delete cascade,
  coach_id uuid not null references public.profiles(id) on delete cascade,
  note text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index coach_athlete_notes_connection_id_idx
  on public.coach_athlete_notes (connection_id);

alter table public.coach_athlete_notes enable row level security;

create policy "Coach can manage own notes"
  on public.coach_athlete_notes
  for all
  using (auth.uid() = coach_id)
  with check (
    auth.uid() = coach_id
    and exists (
      select 1 from public.coach_athlete_connections c
      where c.id = connection_id
        and c.coach_id = auth.uid()
        and c.status = 'accepted'
    )
  );
