# Analysis workflow audit — upload → FastAPI → report

Written before any implementation work in this pass. State as of commit `80b9a2e` on `main`.

---

## 1. Upload flow trace (wizard → Supabase Storage → `performances` table)

Entry point: `frontend/src/features/performances/wizard/ReviewStep.tsx` → `handleCreatePerformance()` → `useCreatePerformance().mutateAsync({ athleteId, draft })`.

`useCreatePerformance` (`frontend/src/features/performances/hooks/useCreatePerformance.ts`), inside one `useMutation` `mutationFn`, currently does **four sequential steps**:

1. `uploadPerformanceRecording(athleteId, file)` — `performance.service.ts`. Uploads the raw `File` to Supabase Storage bucket `performance-recordings` at path `{athleteId}/{uuid}.{ext}`. Bucket confirmed **private** this session (`GET /storage/v1/object/public/...` → `404 Bucket not found`, the standard Supabase response for a non-public bucket).
2. `createPerformanceRecord(athleteId, draft, videoPath)` — inserts a row into `performances` with `upload_status: "uploaded"`, `video_url: videoPath` (the Storage object path, not a URL). Returns `{id, performance_number}`.
3. `submitVideoForAnalysis(draft.recording)` — re-uploads the **same in-memory `File` object a second time**, this time as multipart form data directly to the FastAPI backend's `POST /api/analyze/video`. **This is the integration gap** — see §3.
4. `updatePerformanceAnalysis(data.id, {...})` — writes `analysis_job_id` (or `analysis_error` on failure) back onto the same row via `.update().eq("id", performanceId)`.

Navigation to `/console/athlete/performances/{id}/processing` happens only after all four steps resolve (or the try/catch in step 3-4 absorbs a backend-submission failure without failing the whole mutation).

**Confirmed via live testing this session** (not just reading code):
- Storage upload path pattern (`{athleteId}/...`) plus a Storage RLS policy already lets the authenticated athlete mint a signed URL for their own object (`POST /storage/v1/object/sign/performance-recordings/{path}` → `200`, and the returned signed URL successfully downloaded the real file, 577,072 bytes).
- Querying `performances` with **no `athlete_id` filter at all** (authenticated as the test athlete) returned only that athlete's 8 rows — consistent with, though not conclusive proof of, RLS enforcing `athlete_id = auth.uid()` on `SELECT`. Policy text itself is being independently verified (§2).
- `performances.upload_status` has a `CHECK` constraint allowing exactly `{uploaded, analyzing, completed, failed}` (discovered and worked around in the previous session — not `"processing"`).

## 2. FastAPI async analysis API trace

`backend/app/api/routes.py`, mounted at `/api`:

- `POST /api/analyze/video` — `multipart/form-data`, field `file`. Validates `content_type` in `{video/mp4, video/quicktime, video/webm}` (415 otherwise). Saves upload to `backend/temp/{uuid}.{ext}`, creates a `Job` in the **in-memory** `job_store` (`app/services/jobs/store.py`, `threading.Lock`-guarded dict, not persisted, lost on server restart), schedules `_run_analysis_job` via `BackgroundTasks`, returns `202 {job_id, status: "queued"}` immediately (measured ~85-135ms).
- `_run_analysis_job` (background thread): `mark_processing` → `analyze_video(path)` (the RTMPose live pipeline) → `mark_completed(job_id, result)` or `mark_failed(job_id, str(error))` in a try/except, `finally: video_path.unlink()`. A job **never** gets stuck in `queued` forever due to an exception — every path reaches a terminal state or the process dies.
- `GET /api/analyze/video/{job_id}` — returns `job.to_dict()` (`{job_id, status, created_at, updated_at, result, error}`); `404` if the job id is unknown (e.g., server restarted, or the id was fabricated/guessed).
- **No authentication of any kind on either endpoint.** No verification that the caller is who they claim to be, no association between a job and a Supabase user. This is pre-existing (documented in `docs/ENGINEERING_HANDOFF.md` §11 "No authentication, rate limiting, or file-size limits") and out of scope to fully fix here — see §3 for how this interacts with the new work.
- `job_store.prune_finished_older_than(minutes=60)` runs on every new submission — old completed/failed jobs are dropped from memory after an hour. A completed job's `analysis_result` is safe from this because the frontend persists it into Supabase on completion; the FastAPI job store itself is not the durable copy.

Full completed-job result shape (per `docs/ENGINEERING_HANDOFF.md` §6, confirmed again this session against two real jobs):
```
{ provider, video: {total_frames, fps, duration_seconds},
  analysis: {frames_with_pose, detection_rate_percent},
  recording_quality: {...full quality gate...},
  tracking_summary: {...},
  biomechanics: {status: "skipped", reason} | {provider, fps, segments: [...]} }
```

## 3. The exact integration gap

**The browser currently transmits the full video file twice**: once to Supabase Storage (durable), once directly to FastAPI (ephemeral, deleted after analysis). This has four concrete consequences, each mapped to a numbered requirement from the task:

1. **No way to (re)trigger analysis without the original in-memory `File`.** Once the wizard unmounts, `draft.recording` is gone. Revisiting an old performance from history and clicking "Retry" has nothing to re-submit — today there is no retry UI at all (requirement #8 "retry available" is entirely unimplemented).
2. **Double upload bandwidth from the client**, proportional to video size, on every submission — the same bytes leave the browser twice.
3. **Submission is entangled with the creation mutation.** There's no standalone "submit this existing performance's video for analysis" operation, which is what a retry button needs.
4. **The task explicitly asks me to evaluate a signed-URL/authenticated-download alternative before writing more code** (its own numbered pre-implementation instruction) — this session's testing (§1) confirms the athlete's session can already mint a short-lived signed URL for their own uploaded object via existing Storage RLS, with no policy changes needed. That signed URL can be handed to FastAPI, which downloads the video server-side instead of receiving it from the browser a second time.

**Decision** (elaborated with full rationale as its own task before implementation): move video transfer to FastAPI from **browser re-upload** to **server-side download via a short-lived Supabase Storage signed URL**. The bucket stays private; no new Storage policies are needed (the athlete's own read/sign access already works); a new FastAPI endpoint is added rather than overloading the existing multipart one. SSRF is the main new risk this introduces on the backend and needs explicit host/path/scheme validation before this is safe to ship — see the architecture decision doc section for full mitigation.

**Duplicate-submission risk, current state**: the "Create Performance" button disables on `createPerformance.isPending`, but that's a `useMutation`-driven boolean that only flips on the *next* React render — a fast double-click before that render commits can start two concurrent `mutationFn` calls (two Storage uploads, two `performances` rows, two backend jobs). `useAnalysisPolling`'s completion-persisting `useEffect` also has no idempotency guard, so React 19 `StrictMode`'s dev-only double-invoke can fire it twice for the same terminal state (harmless — same values written twice — but not clean). Both need explicit guards (requirement #9).

**RLS verification status**: empirical single-account testing (§1) is consistent with per-user isolation on `performances` `SELECT`, but is not proof — a single-tenant table with no other rows would look identical whether or not RLS is enforced. Definitive verification requires reading the actual policy text; the user is fetching `pg_policies` for the `performances` table for this reason. Implementation below proceeds without weakening or replacing any existing policy, and does not add anything that would bypass RLS.

---

## 4. Architecture decision: signed-URL server-side download

**Chosen**: add `POST /api/analyze/video-url` (JSON body `{"video_url": "..."}`) alongside the existing file-upload endpoint. The frontend, instead of re-uploading the raw `File`, calls `supabase.storage.from("performance-recordings").createSignedUrl(path, expiresInSeconds)` for the athlete's own already-uploaded object (confirmed working, §1) and sends that URL to the new endpoint. FastAPI downloads the video itself (via `httpx`, already a dependency — used by `RTMPoseWorkerClient`) into the same `temp/{uuid}{suffix}` path the existing endpoint uses, then reuses the exact same `_run_analysis_job` background pipeline unchanged.

**Rejected alternative**: keep browser-side re-upload as the only mechanism. Rejected because it structurally cannot support retry from a page that doesn't have the original `File` in memory (performance history, a reloaded detail page), and every submission doubles client upload bandwidth for no benefit — the bytes already exist in Storage.

**Rejected alternative**: make the `performance-recordings` bucket public and have FastAPI fetch the public URL. Explicitly excluded by the task. Also strictly worse than the signed-URL approach for no implementation savings — the signed-URL path was already confirmed working with zero policy changes.

**New risk this introduces: SSRF.** `POST /api/analyze/video-url` accepts a URL from the client and has the server fetch it — a textbook SSRF vector if unconstrained (a malicious caller could pass `http://169.254.169.254/...`, an internal service address, etc.). Mitigations, enforced before any network call is made:
- **Host allowlist**: the URL's host must exactly equal the configured Supabase project host (from `SUPABASE_URL`, e.g. `hdtrkuhjzvmywneodeiq.supabase.co`). Anything else is rejected with `400` before any request is issued.
- **Path prefix check**: the path must start with `/storage/v1/object/sign/performance-recordings/`. Rejects attempts to redirect the fetch at some other Supabase REST/Auth/Storage endpoint on the same host.
- **Scheme check**: `https` only.
- **No redirect following**: `httpx` does not follow redirects by default; left as default (`follow_redirects` not set), so a crafted redirect response can't be used to pivot to a different host.
- **Bounded download**: streamed to disk with a max-size cutoff (reuses the same order-of-magnitude limits implied by real sprint clips, generous enough for a real upload, not unbounded) and a request timeout, so a slow-loris or oversized response can't tie up a background thread indefinitely.
- **This validates the URL's *destination*, not the signed token's validity** — an expired or tampered signed URL still fails, just later (Supabase itself rejects it with a 400/403 on the actual GET, which is surfaced as a failed job with a clear error, the same as any other download failure).

**What this does *not* solve**: FastAPI still has no authentication layer of its own (pre-existing, §2/§3). Isolation between users is achieved because (a) only the owning athlete's authenticated Supabase session can mint a signed URL for their own Storage object (Storage RLS, unchanged), and (b) the resulting `job_id` is an unguessable UUID stored only in that athlete's RLS-protected `performances` row. Nothing about this change weakens that; nothing about it adds real backend-level authorization either. That remains a residual limitation or a real auth story is added to FastAPI itself (out of scope here — see final report).

---

## 5. Implementation summary (what was actually built)

- **Backend**: `POST /api/analyze/video-url` (`backend/app/api/routes.py`) — same job pipeline as the existing file-upload endpoint, downloads server-side via `httpx` after `_validate_signed_video_url`'s host/path/scheme allowlist. 8 new tests in `backend/tests/test_analyze_video_route.py` (SSRF-guard rejections, success path, download failure, oversized download) — 302/302 backend tests passing.
- **Frontend**: `analysis.service.ts` gained `createSignedVideoUrl`, `submitVideoUrlForAnalysis`, `startAnalysisForStoredVideo` (mint-and-submit in one call); `submitVideoForAnalysis` (raw re-upload) removed, nothing calls it anymore. `useCreatePerformance` and new `useRetryAnalysis` both go through `startAnalysisForStoredVideo`.
- **Duplicate-submission guards**: synchronous `useRef` locks in `ReviewStep`'s create handler and inside `useRetryAnalysis`, closing the double-click race that a `mutation.isPending`-driven `disabled` prop alone doesn't close (it only updates on the next render). Page refresh cannot resubmit anything by construction - submission only happens from an explicit button handler, never an effect.
- **Bounded polling**: `useAnalysisPolling` stops on `completed`/`failed`, on a 10-minute elapsed timeout (does not mark the row failed on timeout - the backend job may still finish), and naturally on unmount via react-query's inactive-query behavior. A `useRef`-keyed guard stops the terminal-state Supabase write from firing twice under `StrictMode`'s dev-only double-invoke.
- **Explicit UI states**: `PerformanceProcessing.tsx`'s `deriveState` (exported, unit-tested) maps `{upload_status, live job status, timed-out}` to one of `queued | processing | completed | failed | timed_out | not_started`, each with distinct copy/styling. `PerformanceDetail.tsx` renders completed/failed/pending distinctly, including a **Retry Analysis** button on `failed`.
- **Tests added**: `backend/tests/test_analyze_video_route.py` (+8), `frontend/.../pages/deriveState.test.ts` (10 cases covering every named state plus priority-ordering edge cases). Existing `AnalysisReport.test.tsx` (6 cases) untouched and still passing.
- **Verified live in-browser** (not just unit tests): performance #07 set to a simulated `failed` state, real **Retry Analysis** click → real signed URL minted via Supabase Storage → real `POST /api/analyze/video-url` (202) → real server-side download + RTMPose analysis → real completion → `PerformanceProcessing` showed the live queued/processing/completed states → `PerformanceDetail` rendered the finished report. Numbers matched the same clip's previously-recorded benchmark exactly (100% detection, 12.1s, Side View, biomechanics correctly skipped for ankle/feet visibility) - the actual analysis pipeline is untouched by any of this session's changes, only how the video reaches it.
- **Bug caught during this verification**: the main FastAPI process had been started without `--reload` in an earlier session, so it kept serving the pre-existing code and returned `404` for the new route until restarted. Not a code defect, but a reminder for whoever runs this locally - restarted with `--reload` this time.
- **RLS confirmed via `pg_policies`** (not just empirical single-account testing): `performances` has exactly three policies, all `auth.uid() = athlete_id` - `SELECT` (`qual`), `INSERT` (`with_check`), `UPDATE` (`qual`). A user genuinely cannot read or update another user's row at the database level.
- **New finding from that same policy text**: the `UPDATE` policy's `with_check` is `null`. `qual` correctly restricts which existing rows can be targeted (must already belong to the caller), but nothing restricts what the row is allowed to become afterward - an authenticated user could `UPDATE performances SET athlete_id = '<someone-else>' WHERE id = <a row they own>`, reassigning their own row to another `athlete_id`. This cannot be used to touch another user's *existing* data (the `USING` clause still gates that), but it is a real gap (silent ownership transfer of one's own rows). Not fixed - would require adding `WITH CHECK (auth.uid() = athlete_id)` to the existing `UPDATE` policy, which needs the project owner to run it, same as the original migration.
