-- Profile photo upload (see docs/ENGINEERING_HANDOFF.md - deferred during
-- Athlete Console completion, closed as its own follow-up).
--
-- Private bucket, not public: the coach-connection model (migration 0005)
-- gates ALL athlete data behind an accepted connection - a public avatars
-- bucket would let anyone with the URL view an athlete's photo with zero
-- relationship to them, which is a real problem given this platform's
-- repeated, explicit concern about apparent-minors' data. Same folder-
-- scoped ownership pattern already proven for performance-recordings.
--
-- Storage key is fixed per user ({user_id}/avatar, no extension - the
-- client sets contentType explicitly on upload) with upsert:true, so a
-- re-upload always replaces the same object instead of accumulating
-- orphaned files.
--
-- Run this once in the Supabase SQL editor for this project.
--
-- Rollback:
--   drop policy if exists "Users can delete their own avatar" on storage.objects;
--   drop policy if exists "Users can update their own avatar" on storage.objects;
--   drop policy if exists "Users can upload their own avatar" on storage.objects;
--   drop policy if exists "Users can view their own avatar" on storage.objects;
--   delete from storage.buckets where id = 'avatars';

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('avatars', 'avatars', false, 5242880, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do nothing;

create policy "Users can view their own avatar"
  on storage.objects
  for select
  using (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "Users can upload their own avatar"
  on storage.objects
  for insert
  with check (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "Users can update their own avatar"
  on storage.objects
  for update
  using (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text)
  with check (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "Users can delete their own avatar"
  on storage.objects
  for delete
  using (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);
