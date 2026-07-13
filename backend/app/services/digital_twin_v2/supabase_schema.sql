create table if not exists public.athlete_twin_sessions (
    id uuid primary key default gen_random_uuid(),
    athlete_id uuid not null,
    performance_id uuid not null,
    session_id uuid null,
    event text not null,
    recorded_at timestamptz not null,
    features jsonb not null default '{}'::jsonb,
    confidences jsonb not null default '{}'::jsonb,
    context jsonb not null default '{}'::jsonb,
    schema_version text not null default '1.0.0',
    created_at timestamptz not null default now()
);

create index if not exists athlete_twin_sessions_athlete_event_time_idx
on public.athlete_twin_sessions (
    athlete_id,
    event,
    recorded_at desc
);

alter table public.athlete_twin_sessions enable row level security;

create policy "athletes can read own twin sessions"
on public.athlete_twin_sessions
for select
using (auth.uid() = athlete_id);

create policy "athletes can insert own twin sessions"
on public.athlete_twin_sessions
for insert
with check (auth.uid() = athlete_id);
