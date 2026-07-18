-- Adds performance_type to the performances table. The wizard's step 2
-- (PerformanceTypeStep.tsx) already asks the athlete to choose one of
-- practice / competition / trial / assessment and stores it in the local
-- wizard draft (PerformanceDraft.performanceType) - but createPerformanceRecord
-- (performance.service.ts) never sent it to the database, so the value was
-- silently discarded on every submission until this migration.
--
-- Nullable, not required: existing rows (and any future insert that omits
-- it) simply have no type - callers should not assume this column is always
-- populated.
--
-- Run this once in the Supabase SQL editor for this project
-- (no service-role credentials are available to the coding agent to run
-- this automatically).

alter table public.performances
  add column if not exists performance_type text;

alter table public.performances
  add constraint performances_performance_type_check
  check (performance_type in ('practice', 'competition', 'trial', 'assessment'));

comment on column public.performances.performance_type is
  'Athlete-selected session type from the upload wizard (PerformanceTypeStep.tsx): practice, competition, trial, or assessment. Null for rows created before this column existed.';
