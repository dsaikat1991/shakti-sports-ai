-- Closes a gap found while auditing RLS for the analysis workflow (see
-- docs/ANALYSIS_WORKFLOW_AUDIT.md section on RLS verification).
--
-- performances' existing UPDATE policy ("Athletes can update own
-- performances") only has a USING clause (auth.uid() = athlete_id),
-- which correctly restricts *which* rows an athlete can target, but has
-- no WITH CHECK clause restricting what the row is allowed to become
-- afterward. Confirmed via pg_policies:
--
--   cmd: UPDATE, qual: (auth.uid() = athlete_id), with_check: null
--
-- Without a WITH CHECK, an authenticated athlete could run:
--   UPDATE performances SET athlete_id = '<someone-else>' WHERE id = <a row they own>
-- silently reassigning their own row to another athlete_id. This cannot
-- be used to touch another user's *existing* data (USING still gates
-- that), but it's a real gap - a silent ownership transfer of one's own
-- rows, which would then make that row invisible to its original owner
-- and (depending on what else references it) potentially orphaned.
--
-- ALTER POLICY only touches the clause(s) you specify - the existing
-- USING clause is left exactly as-is; this only adds the missing check.
--
-- Run this once in the Supabase SQL editor for this project.

alter policy "Athletes can update own performances"
  on public.performances
  with check (auth.uid() = athlete_id);
