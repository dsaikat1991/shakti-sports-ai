-- Backstop for the /contact form (frontend/src/app/pages/Contact.tsx).
-- The form's primary action is a mailto: link (works today, zero infra),
-- but that depends on the visitor having a configured email client - if
-- that fails, the message is lost with no trace. This table captures
-- every submission regardless, as a durable record.
--
-- The contact page is public (unauthenticated visitors can reach it), so
-- INSERT must be allowed for the anon role, not just authenticated users.
-- No SELECT policy is granted to anon/authenticated - only the project
-- owner (via the Supabase dashboard, which uses service-role access and
-- bypasses RLS) can read submissions. This prevents visitors from
-- enumerating other people's messages.
--
-- No notification mechanism exists yet - new rows just sit here until
-- someone checks the Supabase dashboard's Table Editor. Revisit if this
-- becomes a real support channel (e.g. a Database Webhook to an email
-- service) rather than an occasional-inquiry form.
--
-- Run this once in the Supabase SQL editor for this project.

create table if not exists public.contact_submissions (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text not null,
  subject text,
  message text not null,
  created_at timestamptz not null default now()
);

alter table public.contact_submissions enable row level security;

create policy "Anyone can submit a contact message"
  on public.contact_submissions
  for insert
  to anon, authenticated
  with check (true);
