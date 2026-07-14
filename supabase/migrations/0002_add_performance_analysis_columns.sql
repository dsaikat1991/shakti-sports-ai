-- Adds columns needed to persist the FastAPI backend's async video-analysis
-- job (see backend/app/api/routes.py POST/GET /api/analyze/video) onto the
-- existing performances row, so results survive page reloads and are
-- visible across devices instead of living only in browser localStorage.
--
-- upload_status already exists and the frontend already has UI for
-- "uploaded" / "analyzing" / "completed" / "failed" values (see
-- PerformanceDetail.tsx, PerformanceHistory.tsx, PerformanceProcessing.tsx)
-- - this migration reuses that column for the analysis lifecycle rather than
-- introducing a second, parallel status column.
--
-- NOTE (discovered while wiring the frontend up to this table): the table
-- has an existing CHECK constraint, performances_upload_status_check, whose
-- allowed values are exactly {uploaded, analyzing, completed, failed} - NOT
-- "processing". This isn't version-controlled anywhere else in the repo
-- (see docs/ENGINEERING_HANDOFF.md section 5 - schema isn't fully checked
-- in), so it's easy to reintroduce this exact bug by adding a "processing"
-- state later. Use "analyzing" for the in-flight state instead.
--
-- Run this once in the Supabase SQL editor for this project
-- (no service-role credentials are available to the coding agent to run
-- this automatically).

alter table public.performances
  add column if not exists analysis_job_id text,
  add column if not exists analysis_result jsonb,
  add column if not exists analysis_error text;

comment on column public.performances.analysis_job_id is
  'Job id returned by POST /api/analyze/video on the FastAPI backend. Null if analysis was never started (e.g. backend was unreachable at upload time).';

comment on column public.performances.analysis_result is
  'Full result payload from a completed analysis job (see ENGINEERING_HANDOFF.md section 6 for shape). Null until upload_status = ''completed''.';

comment on column public.performances.analysis_error is
  'Human-readable error message if upload_status = ''failed'' or analysis could not be started.';
