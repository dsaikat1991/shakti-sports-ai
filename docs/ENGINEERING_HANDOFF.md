# Shakti Sports AI — Engineering Handoff

**Read this document fully before touching code.** It assumes zero memory of prior work. Where something is uncertain, unverified, or was deliberately left broken, that is stated explicitly — do not assume silence means "done and correct."

Last updated: 2026-07-16. Work through commit `5e0d895` on `main` (profile photo upload, §21) is committed and pushed. **§22 (Athlete Console UI/feature pass) is the most recent work and is not yet committed** as of this writing — read §22 first if you're starting fresh, then §21/§20/§18, then the rest for backend/biomechanics depth.

---

## 1. What this project is

Shakti Sports AI is an AI-powered athlete talent-discovery platform for India. Athletes upload performance video; the platform runs pose estimation and biomechanics analysis on it; the resulting data is meant to be visible to scouts and coaches. Target events: **sprint (100m), hurdles (110h), long jump, high jump**. Mission framing: help Indian athletes get discovered regardless of which city/academy they have access to.

Only **sprint** has been built out and validated in any depth. Hurdles/long jump/high jump have code stubs (`app/services/athletics/hurdles.py`, `long_jump.py`, `high_jump.py`) but have never been run against real footage.

---

## 2. Repository layout

Two git worktrees exist on this machine:
- `D:\shaktisportsai` — the **main** worktree, on branch `main`. **This is where all real work happens.** Has a GPU (NVIDIA GTX 1650), CUDA 12.1, and the RTMPose stack installed.
- `D:\shaktisportsai\.claude\worktrees\folder-review-194520` — a separate worktree on a different branch, several commits behind. Do not confuse the two. If you were spawned into the worktree, `cd` to `D:\shaktisportsai` for the real repo.

Top-level directories (`D:\shaktisportsai`):
```
backend/          FastAPI app + all Python services (see §4)
frontend/         React + Vite + Tailwind app (Supabase-backed)
docs/             This file, plus ANALYSIS_WORKFLOW_AUDIT.md (frontend<->backend integration trace, §17)
supabase/         New this session (§17) - migrations/0002-0004 (analysis columns, RLS WITH CHECK fix, contact_submissions). Not run automatically - each was hand-run by the project owner in the Supabase SQL editor.
ai-engine/        Empty placeholder (per README's stated structure, never populated)
datasets/         Empty placeholder
models/           Empty placeholder (not to be confused with backend/models/, which has a real .task file)
server/           Empty placeholder
README.md         One-paragraph project description, minorly stale
```

### Backend folder tree (`backend/`)

```
backend/
  app/
    main.py                      FastAPI app entrypoint, CORS config, mounts router at /api
    api/
      routes.py                  ALL live API routes (see §7)
    services/
      jobs/
        store.py                 In-memory async job store (see §6, §9)
      pose/
        analyzer.py               MediaPipe pipeline (legacy live path, now a fallback)
        detector.py                MediaPipe PoseLandmarker factory
        landmark_usability.py      Shared backend-aware confidence policy (mediapipe vs rtmpose) - CRITICAL FILE, see §8
        landmarks.py, serializer.py, pose_quality_policy.py
      pose_remote/                 RTMPose-side pipeline (the one that's actually live now)
        client.py                  RTMPoseWorkerClient - HTTP client to the separate GPU worker service
        video_pipeline.py          analyze_video_with_tracking() - runs tracked pose inference over a whole video
        athlete_selection.py       AthleteTracker - multi-person selection/tracking state machine
        pose_stream.py             PoseStream/PoseGap - gap detection, interpolation, segment splitting
        biomechanics_bridge.py     Converts UnifiedPoseFrame -> FrameMetrics -> sprint biomechanics analysis
        adapter.py                 to_shakti_landmarks() - raw worker response -> landmark list
        live_analyzer.py           RTMPose-backed equivalent of pose/analyzer.py - THE LIVE PIPELINE for /api/analyze/video
        stride_velocity_bridge.py  Camera-motion-robust velocity signal for sprint phase detection (see §8, §9)
      pose_adapters/                DEAD CODE - see §11
      quality/                     Recording-quality / analysis-readiness scoring (see §6, §8)
        scoring.py                 build_quality_result() - the whole quality gate
        frame_quality.py           brightness/sharpness/fps/camera-height scoring functions
        orientation.py             classify_camera_view() - side/three-quarter/front classification
        visibility.py              calculate_athlete_bounding_box(), body-group visibility scoring
        movement.py                calculate_pose_movement(), calculate_frame_change()
        camera.py, lighting.py, sharpness.py  (smaller helpers)
      biomechanics/                 Core per-frame and per-clip biomechanics math (backend-aware, shared by both pipelines)
        angles.py                   Joint angle calculation (knee/hip/elbow), backend-aware landmark reliability
        cadence.py                  estimate_cadence_from_knee_events()
        contact_events.py           detect_contact_events() - CONFIRMED UNRELIABLE for bad camera angles, see §10/§11
        gait_phase.py                detect_knee_cycle_events(), calculate_knee_symmetry()
        centre_of_mass.py           Weighted landmark-centre proxy, vertical oscillation
        signal_processing.py        prepare_angle_segments(), local Hampel outlier filter
        running_cycle.py             Stride/cycle detection from contact events
        flight_time.py               Flight time and duty factor estimation
        sprint_analyzer.py           build_sprint_biomechanics_preview() - orchestrates the above into one result
        frame_metrics.py             FrameMetrics dataclass (carries `backend` field)
        joint_names.py, posture.py, motion_filter.py, motion_reconstruction.py, arm_drive.py, stride.py (mostly empty/stub), gait_signals.py, gait_event_*.py (v2/v3 variants, mostly unvalidated)
      pose_adapters/models.py       UnifiedPoseFrame / UnifiedKeypoint dataclasses (used throughout)
      athletics/                    Per-event registry + sprint phase detection
        sprint_phase.py             detect_sprint_phases() - acceleration/transition/max-velocity/maintenance/deceleration
        registry.py, router.py, sprint.py, hurdles.py, long_jump.py, high_jump.py, models.py, base.py
      sprint/                       ~40 files, deep sprint-specific engines (stride geometry, propulsion, leg spring, mechanical efficiency, etc.) - see §11 for validation status
        stride_geometry_engine.py   analyze_stride_geometry() - wired to real data this session, not otherwise
        stride_geometry_models.py   FootContactEvent, StrideGeometryContext dataclasses
        (all other files in this directory: UNVALIDATED - built but never run against real footage or checked this session)
      reports/
        sprint_segment_report.py    build_sprint_segment_report() / format_segment_report_text() - the human-readable report builder
        coach.py, scoring.py, recommendations.py    EMPTY STUB FILES (1 line each)
      digital_twin/, digital_twin_v2/, physics/, fusion/, motion/, coach/, talent/, validation/, research/, readiness/, athlete_intelligence/, feature_store/, pipeline/
        UNVALIDATED. Built (substantial code exists in all of these), never exercised against real data, never reviewed this session. Treat as unverified.
  rtmpose_worker/                  SEPARATE FastAPI microservice - GPU pose inference
    app.py                          FastAPI app: /health, /initialize, /infer/image
    core.py                         RTMPoseRuntime - wraps MMPoseInferencer (RTMPose-t model + RTMDet-m detector)
  scripts/                          CLI tools, NOT part of the live API
    analyze_clip.py                 Full tracked-pipeline CLI (video -> timeline JSON / annotated video)
    sprint_report.py                Full pipeline CLI including biomechanics report
    benchmark_rtmpose.py, smoke_test_worker.py
  tests/                            294 passing tests (pytest)
    fixtures/ground_truth_contact_labels.json   Hand-labeled ground truth data (see §10)
  examples/                         Test video clips (gitignored - see §12 for what's in there)
  models/pose_landmarker_full.task  MediaPipe model file (gitignored)
  requirements.txt                  Main backend deps (mediapipe, fastapi, opencv, etc.) - UTF-16 encoded, unusual
  requirements-worker-extra.txt     Additional deps for the RTMPose worker venv
  rtmpose-constraints.txt           Version pins for RTMPose worker (numpy, opencv)
  pytest.ini                        testpaths = tests (prevents stray directories from breaking collection)
  .venv/                            Python 3.14.6 - main backend, no GPU deps, runs pytest + the API server
  .venv-rtmpose/                    Python 3.11.9 - has torch/mmpose/mmdet, runs ONLY the rtmpose_worker service
```

### Frontend folder tree (`frontend/`)

```
frontend/src/
  app/
    router/AppRouter.tsx           React Router config - see §17, routing fixed up this session
    router/RoleGate.tsx            Role-based route guard (new, §17)
    layouts/                       MarketingLayout, AuthLayout
    pages/HomePage.tsx, About.tsx, Mission.tsx, Contact.tsx, NotFound.tsx  (About/Mission/Contact/NotFound new, §17)
  features/
    auth/                          Sign in/up, role selection, onboarding - athlete/coach/academy all routed now (§17)
    athlete/                       Dashboard (AthleteLayout - all 7 nav links now resolve, 5 to ComingSoon placeholders, §17)
    performances/                  Upload wizard, performance history/detail/report pages - now wired to the FastAPI backend, see §17
    contact/                       New (§17) - contact form's Supabase backstop service
    home/                          Marketing page sections
  components/ui, layout, shared    Design system components (ComingSoon.tsx new/generalized, §17)
  constants/routes.ts, navigation.ts, roleNavigation.ts
  lib/supabase.ts                  Supabase client init
  theme/                           Design tokens
```

**Outdated as of §17 - kept for history.** At the time this paragraph was written, the frontend only talked to Supabase and never called the FastAPI backend. **That is no longer true.** The frontend now submits videos for analysis via a signed Storage URL, polls for job status, persists results back onto the `performances` row, and renders the real report. See §17 for the full picture and `docs/ANALYSIS_WORKFLOW_AUDIT.md` for the detailed trace/architecture decision.

---

## 3. High-level architecture

**Diagram below predates §17's frontend integration work - see §17 for the current, accurate data flow (browser → Supabase Storage signed URL → FastAPI → RTMPose worker → back onto the `performances` row).** Kept here for the backend-internal pipeline detail, which is still accurate.

```
                        ┌─────────────────────────┐
   Browser  ──────────▶ │  Frontend (React/Vite)   │
                        └───────────┬─────────────┘
                                    │ (direct calls, NOT via backend)
                                    ▼
                        ┌─────────────────────────┐
                        │   Supabase (Postgres +   │
                        │   Auth + Storage)         │
                        └─────────────────────────┘

                        ┌─────────────────────────┐
   curl/Postman ──────▶ │  FastAPI backend          │  (nothing currently calls this except manual testing)
                        │  (.venv, Python 3.14)     │
                        └───────────┬─────────────┘
                                    │ POST /api/analyze/video
                                    ▼
                        ┌─────────────────────────┐
                        │  Async job (in-memory)    │
                        │  runs live_analyzer.py    │
                        └───────────┬─────────────┘
                                    │ per-frame HTTP calls
                                    ▼
                        ┌─────────────────────────┐
                        │  rtmpose_worker service   │  SEPARATE PROCESS, must be started manually
                        │  (.venv-rtmpose, GPU)     │  `uvicorn rtmpose_worker.app:app --port 8011`
                        │  RTMPose-t + RTMDet-m      │
                        └─────────────────────────┘
```

Two independent pose pipelines exist in the codebase:

| | MediaPipe path | RTMPose path |
|---|---|---|
| Entry point | `app/services/pose/analyzer.py` | `app/services/pose_remote/live_analyzer.py` |
| Where it runs | In-process, CPU | Separate GPU-backed microservice, called over HTTP |
| Multi-person tracking | No — takes `result.pose_landmarks[0]` (first detected pose only) | Yes — `AthleteTracker` (selection/tracking/coasting/reselection state machine) |
| Gap interpolation | No | Yes — `pose_stream.fill_gaps()` |
| Currently wired to `/api/analyze/video`? | No (available as fallback, not auto-selected) | **Yes — this is the live pipeline** |
| Needs GPU/separate process running? | No | **Yes** — will fail cleanly with a clear error if `rtmpose_worker` isn't running |

Both pipelines feed into the **same shared biomechanics code** (`app/services/biomechanics/*`, `app/services/quality/*`), which is backend-aware (accepts `backend="mediapipe"` or `backend="rtmpose"` and branches confidence thresholds accordingly). Fixing something in `biomechanics/` fixes it for both paths.

---

## 4. Subsystems

### 4.1 Pose estimation
- **RTMPose worker** (`rtmpose_worker/`): `rtmpose-t_8xb1024-700e_body8-halpe26-256x192` model (RTMPose-tiny, Halpe26 26-keypoint schema) + `rtmdet_m_640-8xb32_coco-person` detector (RTMDet-medium, person-only, COCO+Objects365 pretrained). Confirmed via direct inspection this session (see §9) — this is genuine MMDetection, not a stub.
- **MediaPipe** (`app/services/pose/detector.py`): standard MediaPipe Pose Landmarker, in-process.

### 4.2 Multi-person tracking (RTMPose path only)
`app/services/pose_remote/athlete_selection.py`. `select_primary_athlete()` scores each detected person by bounding-box area (40%), centre proximity (25%), pose confidence (20%), landmark completeness (15%) and picks the best. `AthleteTracker` then tracks that person frame-to-frame via `match_components()` (bbox overlap, centre motion, size similarity, landmark similarity, track-id match), with states: `selected` → `tracked` → `coasting` (briefly lost, up to 5 frames) → `reselected` (lost too long) → `lost`.

### 4.3 Gap handling
`app/services/pose_remote/pose_stream.py`. Non-observed (coasting/lost/error) frames become `PoseGap`s. `fill_gaps()` linearly interpolates gaps shorter than `max_gap_ms` (default 300ms); longer gaps are left as real discontinuities. `split_into_segments()` then splits the stream at any remaining unfilled gap — this correctly represents real editing cuts / long occlusions rather than pretending motion is continuous across them.

### 4.4 Biomechanics engine
`app/services/biomechanics/`. Computes, per continuous segment: joint angles (knee/hip/elbow), cadence (via knee-flexion cycle detection), ground contact/flight time/duty factor (via foot-height trajectory), knee symmetry, centre-of-mass vertical oscillation. Orchestrated by `sprint_analyzer.build_sprint_biomechanics_preview()`.

### 4.5 Quality / analysis-readiness gate
`app/services/quality/`. Scores: pose detection rate, lighting, sharpness, fps, full-body visibility, athlete movement, camera occupancy (distance), camera angle/rotation (`Side View` required for `biomechanics_ready`), and — new this session — **camera height/tilt** (headroom-based). Produces `warnings`/`recommendations` for the user, and hard-gates whether biomechanics gets computed at all (`biomechanics: {"status": "skipped", "reason": ...}` if not ready).

### 4.6 Sprint-specific report generation
`app/services/reports/sprint_segment_report.py` reshapes the raw biomechanics output into a compact per-segment report (cadence, stride frequency, ground contacts, flight time, duty factor, knee symmetry, per-joint angle mean/min/max/coverage). `app/services/sprint/stride_geometry_engine.py` (existed already, wired to real data this session via `pose_remote/stride_velocity_bridge.py`) computes step length, symmetry, crossover rate from contact events.

### 4.7 Sprint phase detection
`app/services/athletics/sprint_phase.py`. `detect_sprint_phases()` takes a `timestamps_ms` + `horizontal_progression` (position-like) series, differentiates it into velocity/acceleration, and segments into acceleration → transition → maximum_velocity → maintenance → deceleration.

### 4.8 Async job processing
`app/services/jobs/store.py`. In-memory `JobStore` (thread-safe, `threading.Lock`), FastAPI `BackgroundTasks` runs the actual analysis in Starlette's threadpool. See §6 for the API contract, §11 for limitations.

### 4.9 Frontend
Standard React/Vite/Tailwind SPA, Supabase for auth/storage/DB, React Router, TanStack Query, Zustand-style wizard store for the performance upload flow. Not connected to the backend (see §2).

### 4.10 Everything under `backend/app/services/{digital_twin,digital_twin_v2,physics,fusion,motion,coach,talent,validation,research,readiness,athlete_intelligence,feature_store,pipeline}/`
Substantial code exists (dozens of files). **None of it has been touched, reviewed, or validated this session.** Do not assume it works. Do not assume it doesn't. It's simply unknown — treat any claim about it as unverified until checked.

---

## 5. Database schema

**This is not fully version-controlled in the repo.** Only one table has a checked-in schema file:

`backend/app/services/digital_twin_v2/supabase_schema.sql`:
```sql
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
-- + RLS policies restricting read/insert to auth.uid() = athlete_id
```

**Update (this session): the rest of the schema below is now CONFIRMED via direct introspection** (a one-shot `information_schema`/`pg_policies`/`pg_constraint`/`storage.buckets` query run by the project owner in the Supabase SQL editor - see `docs/ANALYSIS_WORKFLOW_AUDIT.md` for the exact query and the RLS-specific findings), not inferred from frontend code as before. It is still not checked into the repo as a migration file - the action item below still stands - but it is no longer a guess.

- **`profiles`** — `id` (uuid, fk to `auth.users`, cascade delete), `role` (text, `CHECK` constrained to `athlete`/`coach`/`academy`/`admin`), `full_name`, `email`, `avatar_url`, `phone`, `state`, `district`, `is_verified` (bool, default false), `created_at`, `updated_at`. RLS: `SELECT`/`UPDATE`/`INSERT` all restricted to `auth.uid() = id`.
- **`athlete_profiles`** — `id` (fk to `profiles`, cascade), `date_of_birth`, `gender`, `height_cm`, `weight_kg`, `preferred_event`, `secondary_event`, `academy`, `bio`, `dominant_leg`, `personal_best`, `created_at`. Same RLS pattern (`auth.uid() = id`).
- **`coach_profiles`** — `id` (fk to `profiles`, cascade), `organization`, `designation`, `experience_years`, `specialization`, `verified` (bool, default false), `bio`, `created_at`. Same RLS pattern. Wired up to real onboarding UI this session (`CoachOnboarding.tsx`) - previously existed unused.
- **`academy_profiles`** — `id` (fk to `profiles`, cascade), `academy_name`, `address`, `website`, `description`, `verified` (bool, default false), `created_at`. Same RLS pattern. Wired up to real onboarding UI this session (`AcademyOnboarding.tsx`) - previously existed unused.
- **`events`** — `id`, `name` (e.g. `"Sprint"`, `"Hurdles"`, `"Long Jump"`, `"High Jump"`), `category`, `is_active` (bool, default true), `created_at`. RLS: `SELECT` restricted to `is_active = true`. Looked up by name from `EVENT_NAME_MAP` in `performance.service.ts`.
- **`performances`** — `id`, `athlete_id` (fk to **`athlete_profiles`**, not `profiles` directly - cascade delete), `event_id` (fk to `events`), `title`, `performance_date` (default `CURRENT_DATE`), `attempt_number` (default 1), `video_url`, `thumbnail_url`, `duration_seconds`, `file_size_mb`, `upload_status` (text, `CHECK` constrained to `draft`/`uploaded`/`analyzing`/`completed`/`failed`, default `'draft'` though the app always inserts `'uploaded'` explicitly), `notes`, `created_at`, `updated_at`, `performance_number`, plus `analysis_job_id`/`analysis_result` (jsonb)/`analysis_error` added this session (see §16 follow-up work, migrations `0002`/`0003`). RLS: `SELECT`/`INSERT`/`UPDATE` all `auth.uid() = athlete_id`, `UPDATE` has both `USING` and `WITH CHECK` (the latter added this session - see migration `0003` - closing a gap where an athlete could reassign their own row to a different `athlete_id`).
- **`analysis_reports`** — `id` (uuid, default `gen_random_uuid()`), `performance_id` (fk to `performances`, cascade), `performance_score` (numeric), `confidence` (numeric), `analysis` (jsonb), `created_at`. RLS: **`SELECT` only** (`"Athletes can view own analysis reports"`, scoped via `EXISTS (... performances.athlete_id = auth.uid())`) - **no `INSERT` policy exists**. See "Architectural decision: `analysis_reports` vs `performances.analysis_result`" below - this table is currently unused by any code path (confirmed via repo-wide search this session) and is reserved for a future feature, not a bug to fix.
- **Storage bucket**: `performance-recordings` — **confirmed private** (`public: false`), `allowed_mime_types: [video/mp4, video/webm, video/quicktime]` (enforced at the Storage layer itself, not just FastAPI's own content-type check), no `file_size_limit` set. RLS on `storage.objects`: authenticated users can `INSERT`/`SELECT` only where `bucket_id = 'performance-recordings' AND (storage.foldername(name))[1] = auth.uid()::text` - i.e. only within their own `{athleteId}/` folder. No `UPDATE`/`DELETE` storage policies exist (no replace/delete UI exists in the app either, so this hasn't been a gap in practice).

**Action item for whoever picks this up:** the schema above is now confirmed accurate, but still isn't checked into the repo as an actual migration file beyond `backend/app/services/digital_twin_v2/supabase_schema.sql` and this session's `supabase/migrations/0002_*`/`0003_*`. Consider running `supabase db dump` (or exporting from the dashboard) to check in the full baseline schema, so the database can be recreated from this repo alone.

### Architectural decision: `analysis_reports` vs `performances.analysis_result` (this session)

Two tables could plausibly hold "the AI analysis result" for a performance. The decision made this session, after discovering `analysis_reports` existed and was unused:

1. **`performances.analysis_result`/`analysis_job_id`/`analysis_error`** (added this session, migration `0002`) is the current source of truth for: upload status, analysis-job state (queued/analyzing/completed/failed), the full raw quality-gate output, tracking output, biomechanics output, and error messages. This is inherently workflow/job-lifecycle state, which is why it lives directly on the `performances` row rather than a separate table.
2. **`analysis_reports`** (`performance_score`, `confidence`, `analysis` jsonb) is a differently-shaped table - a distilled score + confidence + payload, one conceptual "report" per performance - that does not correspond to anything the backend currently computes. It matches the shape of **roadmap step 8, "sprint score"** (see §13), which has not been started.
3. **`analysis_reports` is currently unused by design, not by oversight.** A repo-wide search this session found zero references to it in any frontend or backend code.
4. **Its missing `INSERT` RLS policy is not a production bug.** Nothing attempts to write to this table today, so the absence of a write policy has no practical effect. This is different in kind from the `performances` `UPDATE` `WITH CHECK` gap fixed this session (migration `0003`), which *was* an exploitable gap on a table already receiving real writes.
5. **Do not migrate the current raw job result into `analysis_reports`, and do not invent placeholder `performance_score`/`confidence` values to populate it.** When sprint scoring is actually implemented, `analysis_reports` becomes the right home for that distilled output (computed from the raw data already sitting in `performances.analysis_result`), and its RLS (specifically the missing `INSERT` policy) must be reviewed and completed at that time - not before.

---

## 6. API endpoints

Base path: `/api` (mounted in `app/main.py`). CORS currently allows only `http://localhost:5173`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Root health info (name/status) — defined in `main.py`, not `routes.py` |
| GET | `/api/health` | Health check |
| POST | `/api/analyze/video` | Upload a video (multipart, `file` field). Content-type must be `video/mp4`, `video/quicktime`, or `video/webm`. Returns **202** with `{"job_id": "...", "status": "queued"}` immediately — does NOT block for analysis. |
| GET | `/api/analyze/video/{job_id}` | Poll job status. Returns `{job_id, status, created_at, updated_at, result, error}`. `status` is one of `queued`/`processing`/`completed`/`failed`. `result` is populated once `completed`; `error` is a human-readable string once `failed`. 404 if `job_id` unknown. |

**Result shape when `status == "completed"`** (from `live_analyzer.analyze_video()`):
```json
{
  "provider": "rtmpose",
  "video": {"total_frames": int, "fps": float, "duration_seconds": float},
  "analysis": {"frames_with_pose": int, "detection_rate_percent": float},
  "recording_quality": { ...full quality-gate output, see quality/scoring.py's build_quality_result()... },
  "tracking_summary": {"status_counts": {...}, "observed_frames": int, "observed_ratio": float},
  "biomechanics": { "status": "skipped", "reason": "..." }
             /* OR, if recording_quality.biomechanics_ready was true: */
             { "provider": "rtmpose", "fps": ..., "segments": [ {per-segment report, see §4.6} ] }
}
```

No authentication is enforced on these endpoints. No rate limiting. No file size limit beyond what FastAPI/Starlette defaults allow.

---

## 7. Processing pipeline: upload → report (RTMPose path, the live one)

1. Client `POST`s multipart video to `/api/analyze/video`.
2. `routes.py` validates content-type, saves the upload to `backend/temp/{uuid}.{ext}`, creates a `Job` (status=`queued`) in the in-memory store, schedules `_run_analysis_job` via `BackgroundTasks`, returns `{job_id, status}` — this whole step is synchronous but fast (measured ~85-135ms even with a real video).
3. In the background thread: `job_store.mark_processing(job_id)`, then `live_analyzer.analyze_video(video_path)` runs:
   a. **Fast image-quality pass** (`_collect_image_quality`): plain cv2 over every 5th frame — brightness, sharpness, frame-to-frame change. No GPU, no pose inference. Fast regardless of clip length.
   b. **Connect to RTMPose worker** (`_connect_worker`): health check; if unreachable, raises `RuntimeError` with an actionable message — this propagates up and marks the job `failed`, not a server crash.
   c. **Full tracked pipeline** (`analyze_video_with_tracking`): for every frame, encode to JPEG, POST to the worker's `/infer/image`, feed the response through `AthleteTracker.update_from_response()`. This is the slow part — **measured 85-293ms per frame** depending on clip and GPU warm state (a 12-16s clip takes roughly 12s when the worker is already warm, up to ~220s cold).
   d. **Build pose stream** (`timeline_to_pose_stream`) and convert to `FrameMetrics` (`pose_frame_to_frame_metrics`), which computes per-frame joint angles, bounding box, camera view classification.
   e. **Quality signals** derived from the tracked frame data: body-group visibility, occupancy, headroom, camera view, pose movement (frame-to-frame landmark displacement).
   f. **`build_quality_result()`** combines (a) and (e) into the full readiness assessment. If `biomechanics_ready` is false, biomechanics is skipped with a reason; otherwise:
   g. **`analyze_sprint_stream()`** — fills gaps, splits into segments, runs the full biomechanics analysis per segment.
   h. **`build_sprint_stream_report()`** — reshapes into the compact per-segment report.
4. `job_store.mark_completed(job_id, result)` (or `mark_failed` on any exception). Temp file is deleted in a `finally` block regardless of outcome.
5. Client polls `GET /api/analyze/video/{job_id}` until `status` is `completed` or `failed`.

The MediaPipe path (`pose/analyzer.py`) follows the same conceptual shape but runs pose detection in-process, frame by frame, with no tracking/gap-filling — just "first detected pose in each frame."

---

## 8. Algorithms currently in use

- **Pose estimation**: RTMPose-t (top-down, Halpe26 26-keypoint schema) + RTMDet-m detector (live path); MediaPipe Pose Landmarker (fallback path).
- **Multi-person selection**: weighted scoring (bbox area, centre proximity, confidence, landmark completeness).
- **Multi-person tracking**: frame-to-frame matching (bbox IoU, centre-motion, size similarity, landmark similarity, track-id), with a coasting/reselection state machine.
- **Backend-aware landmark confidence policy** (`pose/landmark_usability.py`): MediaPipe uses `visibility >= 0.50 AND presence >= 0.50`; RTMPose uses `confidence >= 0.35` (RTMPose's own detection confidence, not a visibility heuristic). This distinction matters — several bugs this session came from code that didn't use this shared policy.
- **Gap interpolation**: linear interpolation between two observed keypoints across gaps ≤ `max_gap_ms`.
- **Joint angle calculation**: 3-point angle (A-B-C, B is vertex) via dot product / arccos, projected 2D (image-plane), not true 3D.
- **Signal preparation for cyclical biomechanical signals** (`signal_processing.py`): multi-segment extrema detection (NOT single-longest-segment — see bug #1 below) + **local Hampel-style outlier filter** (compares each sample only to its immediate temporal neighbours, not the whole-clip median — see bug #1) + 5-frame moving average smoothing.
- **Cyclical event (peak flexion/extension) detection** (`gait_phase.py`): two-pass — first pass finds every strict turning point vs. immediate neighbours (for location), second pass computes **topographic prominence** relative to the nearest opposite-type turning point (not a fixed narrow window — see bug #1).
- **Cadence estimation**: alternating peak-knee-flexion timestamps → step interval → steps/min, with plausibility filtering (120-1000ms intervals).
- **Ground-contact detection** (`contact_events.py`): local maxima in smoothed foot-height (y-coordinate) trajectory, same two-pass turning-point + prominence approach as cyclical events, with a separate narrow-window prominence just for sizing the contact-duration window. **CONFIRMED UNRELIABLE for some camera angles — see §10, §11.**
- **Stride/running-cycle detection**: same-side contact interval → stride duration/frequency.
- **Stride-based velocity signal for phase detection** (`stride_velocity_bridge.py`, new this session): **same-frame leg-split** (horizontal distance between both ankles within a single frame at a contact event) — chosen specifically because it is camera-motion-invariant, unlike raw on-screen position or cross-time foot-position differences (see §9).
- **Sprint phase segmentation** (`sprint_phase.py`): differentiate position → velocity → acceleration (each 5-frame smoothed), normalize to [0,1] via 5th/95th percentile, threshold-crossing detection for acceleration-end / transition-end / maintenance-start / deceleration-start.
- **Camera view classification** (`quality/orientation.py`): shoulder-width-to-torso-height ratio → Side View / Three-Quarter View / Front View.
- **Camera height/tilt detection** (`quality/frame_quality.py::score_camera_height`, new this session): headroom (empty space above head, from bounding box `y_min`) — empirically thresholded from 3 real clips (see §9, §12).
- **Stride geometry** (`sprint/stride_geometry_engine.py`): step length = horizontal distance between consecutive opposite-foot contact points; various symmetry/stability/crossover scores derived from that.

---

## 9. Every bug fixed this session, and how

All fixes below are on `main`, commits `fbe057a` through `b6b75cf`. Each was verified against real footage, not just unit tests, unless noted.

1. **CLI script import errors** (`ModuleNotFoundError: No module named 'app'`). Root cause: `python scripts/foo.py` puts `scripts/` on `sys.path[0]`, not the project root. Fix: `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` at the top of `analyze_clip.py`, `benchmark_rtmpose.py`, `smoke_test_worker.py`.

2. **`pytest` (no args) failing all 67 test modules.** Root cause: a stray duplicate copy of the whole project (`backend/temp/shakti_rtmpose_live_integration_v20/`, including its own `tests/__init__.py`) collided with the real `backend/tests` package under the same import name, poisoning `sys.modules['tests']`. Fix: added `backend/pytest.ini` with `testpaths = tests`; the duplicate folder was later deleted (confirmed stale/superseded, gitignored anyway).

3. **Cadence/knee-cycle detection totally broken** (0 events on every clip tested). Three compounding causes in `signal_processing.py` / `gait_phase.py`:
   - `prepare_angle_series` kept only the single longest contiguous run of samples, discarding real motion data whenever any gap fragmented the series.
   - `remove_outliers_mad` (global MAD outlier removal) treated genuine peak-flexion values — a numeric minority of any gait cycle — as statistical outliers and stripped them, because it compared each sample to the whole-clip median instead of its local neighbourhood.
   - `_find_local_extrema`'s prominence check compared each candidate peak only to its single adjacent sample; a one-frame wobble near the true peak could shrink apparent prominence to near zero even for a large real swing.
   Fix: multi-segment processing (keep all segments, run extrema detection per-segment instead of discarding all-but-longest); replaced global MAD with a **local Hampel filter** (compares each sample to a small window of neighbours); replaced single-step prominence with **topographic prominence** (distance to nearest opposite-type turning point). Verified: cadence went from complete failure to 187.5 steps/min (46 real events) on a clean clip, matching expectations for a jog.

4. **Ground-contact detection undercounting by ~3x** (14 events found vs. 46 expected from independently-measured cadence). Two causes in `contact_events.py`:
   - A global "must be in the top 25% of the whole clip's foot-height values" gate rejected genuine contacts whenever normal stride variation or camera perspective drift pushed a peak below that bar.
   - Same narrow-window prominence problem as bug #3.
   Fix: same topographic-prominence approach as the knee-cycle fix; removed the global percentile gate. A side effect surfaced immediately: contact *duration* sizing, if left coupled to the now-larger topographic prominence, produced a 94.7% duty factor (a walking gait) — fixed by decoupling duration sizing to use a separate, narrow local-window prominence, while peak *detection* uses the wide-view prominence. Verified: ground contacts went 14→46, matching cadence's 46 events almost exactly; stride frequency (1.56/s) came out to exactly half of steps/s (3.125/s) — the correct step-to-stride ratio.

5. **Backend-aware threshold bypass in three files.** `contact_events.py`, `centre_of_mass.py`, `gait_signals.py`, and (found later, during RTMPose live-wiring) `quality/movement.py::calculate_pose_movement` each had their own hardcoded `visibility >= 0.50 AND presence >= 0.50` check, bypassing the shared `landmark_is_usable()` policy (which correctly uses `confidence >= 0.35` for RTMPose). Fix: added a `backend` field to `FrameMetrics`, threaded `backend` through each function, replaced hardcoded checks with `landmark_is_usable(landmark, backend=backend)`.

6. **`detect_sprint_phases` fed a camera-motion-fragile velocity signal.** Raw on-screen horizontal position only reflects real running speed when the camera is fixed and the athlete moves in a straight line across it. On a real clip, net on-screen progress stalled after ~2s of a 15.7s continuous, steadily-cadenced run (the camera didn't move; the athlete just wasn't covering net ground — a drill, not a straight sprint), which the old signal misread as ~14 continuous seconds of "deceleration." Fix: built `stride_velocity_bridge.py`'s `build_stride_based_progression()` — computes **same-frame leg-split** (both ankles within one frame, at each contact event) instead of cross-time position, then cumulative-sums it as a "distance covered" proxy, fed into the *existing, unmodified* `detect_sprint_phases`. Result: went from an implausible single 14-second deceleration phase to a coherent acceleration-to-peak-then-steady-pace pattern. **Residual limitation, not fixed**: `detect_sprint_phases`'s phase-boundary model still can't distinguish "settled at a new lower pace" from "still decelerating" — once velocity crosses below the maintenance threshold, everything after is labelled deceleration.

7. **Quality gate had no signal for camera height/tilt.** `classify_camera_view` only measures rotation (shoulder/hip width vs. torso height) — confirmed directly that the clip which caused bug #4/#8's underlying camera problem was classified "Side View" at 94-100% confidence on all 787 frames, `suitable_for_sprint: True` throughout. Fix: added `score_camera_height()` (headroom-based, empirically thresholded from 3 real clips), wired into `build_quality_result` as both a scored component and a hard requirement in `biomechanics_ready`.

8. **`/api/analyze/video` would block for 85-220+ seconds per request.** Not viable for a real HTTP endpoint. Fix: `app/services/jobs/store.py` (in-memory job store) + FastAPI `BackgroundTasks`; endpoint now returns in ~100ms with a job ID, client polls for completion.

9. **RTMPose was validated all session but never reachable from the actual API.** Fix: built `pose_remote/live_analyzer.py` (RTMPose-backed equivalent of `pose/analyzer.py`) and swapped it in as the default in `routes.py`. Verified end-to-end against a real running server and real worker — every number (frame counts, detection rate, camera-height score, the specific gating reason) cross-checked against earlier CLI-based findings on the same clip.

---

## 10. Rejected approaches (tried, and specifically why they didn't ship)

For ground-contact detection, after fixing bug #4 above, a deeper problem was found via **visual ground-truth inspection** (not just numeric cross-validation): on a clip shot from a low, close, oblique camera angle, the "detected contact" frames consistently showed the athlete's foot curled up near the glutes — textbook swing/recovery phase, not ground contact. Root cause: for that camera geometry, a curled-up swing foot can foreshorten to project as low in the image (large y) as a genuinely planted foot. This is a wrong-signal problem, not a miscalibration.

Alternatives tried and rejected, each for a specific, verified reason:
- **Ankle/toe velocity local minima** — also fires at the momentary near-zero-velocity pause at the top of the swing arc (like a thrown ball decelerating to zero at its peak), not just at true stance.
- **Peak-knee-extension timing** — too sparse (only ~3 events on a 15-second clip); can't support per-step timing.
- **Centre-of-mass vertical oscillation** — closer (its ~49 local maxima nearly matched the true ~46-step count), but rigorous validation against 4 hand-labeled real gait cycles showed ~120ms mean timing error, against a real contact duration of only 60-150ms — too large to trust, and on close visual inspection the candidate frame still landed inside the swing sequence, not at a confirmed weight-bearing moment.
- **Leg-torso length ratio, cross-time foot-position difference, both-sides leg-split combined** — each explored as camera-motion-robust alternatives during the phase-detection fix (bug #6); the leg-torso ratio showed a real but noisy/overlapping difference between good/bad camera clips (not clean enough for a single-signal classifier — this became the seed for the headroom-based fix instead, see bug #7); cross-time foot-position difference was shown to have the *same* camera-motion fragility as raw position (this is *why* same-frame leg-split was used instead); mixing both sides' leg-split into one signal created artificial zig-zag "acceleration" from a left/right asymmetry in contact timing (unexplained — see §11), so only one consistent side (right) was used.

**The decision made**: rather than ship a sixth unverified heuristic, the confirmed-broken state was documented explicitly in code (`contact_events.py` docstring, `sprint_analyzer.py` limitations list) with the quantified error numbers, and a labeled ground-truth dataset was saved (`tests/fixtures/ground_truth_contact_labels.json`) as a starting artifact for whoever picks this up with more time/data. **Do not re-attempt a quick heuristic fix here without first getting more labeled data or a fundamentally different technical approach** (see §13).

### 10.1 Follow-up session: proper frame-scrubbing tool + expanded ground truth (commit after `c72641a`)

This directly followed up on the "more labeled data" ask above. Built `backend/scripts/label_contact_frames.py` — extracts every individual frame in a window as its own tightly-cropped, upscaled, frame-numbered tile (with the tracked landmark cross-marked) instead of the old compressed static image strip, which the original ground-truth file's own conclusion had flagged as insufficiently rigorous. Used it to re-review 6 events **uniformly sampled across the entire duration** of `my_sprint_2.mp4` (the bad-angle clip), not just 3-4 hand-picked samples as before.

**Findings** (full detail in `tests/fixtures/ground_truth_contact_labels.json`):
- **5 of 6 confirmed false positives**, 1 of 6 confirmed true contact — raises confidence that the swing-vs-stance foreshortening bug is the norm on this camera geometry across the whole clip, not an occasional edge case.
- **Direct proof that calibration cannot fix this**: the one confirmed true contact's peak foot-height signal (normalized_y = 0.9042) is *lower* than one of the confirmed false positives' (0.8971). The two classes overlap on the only signal `contact_events.py` uses — no threshold/prominence tuning can separate them. This upgrades the prior "treat as a wrong-signal problem" hypothesis to a quantified counterexample.
- **New confound found on the "good" clip**: `my_sprint_3.mp4` (the proper side-on, waist-height clip, `camera_height_score: 100`) had a background object (likely a boardwalk post/railing) occluding the tracked leg in 2 of 4 sampled windows, and a uniform brick-paver background gave no reliable ground-plane cue even in unoccluded frames. **A passing camera-angle quality gate does not guarantee labelable footage.** No confident contact label could be produced from this clip this session.
- **New confound found on the archival clip**: `my_sprint.mp4` (low-res B&W stock footage) showed the tracked landmark itself jumping to background clutter in places (a tracking-reliability failure, not a geometric heuristic problem), and includes non-steady-state phases (crouching start, deceleration) the heuristic was never designed for.

**Recommendation carried forward**: do not attempt another foot-height threshold tweak — the overlap evidence rules it out. A real fix needs either a richer feature set (multi-joint configuration/velocity, not single-signal foot height) or a different technical approach, and any further ground-truth collection should screen candidate clips for occlusion and tracking confidence *before* investing labeling effort, not just camera angle.

---

## 11. Known limitations (current, as of `b6b75cf`)

- **Ground-contact timing is not trustworthy for bad camera angles, and this is now quantitatively confirmed, not just suspected.** See §10/§10.1. `contact_time_ms`, `flight_time`, `duty_factor` should not be shown to end users as authoritative numbers until this is properly solved. A direct counterexample (§10.1) proves foot-height threshold recalibration cannot fix it — a confirmed true contact scored lower on the signal than a confirmed false positive.
- **Camera angle, not the algorithm, looks like the dominant variable** for ground-contact accuracy — confirmed the same unmodified detector went from 0/9 (later 1/6 on a wider uniform sample) visually-correct samples on a bad-angle clip to 3/6 on a good-angle clip — but good-angle footage has its *own* unresolved confounds (background occlusion, ambiguous ground-plane texture — see §10.1) that blocked confident labeling this session. "Good camera angle" is necessary but not sufficient for labelable ground truth.
- **Low-quality/archival footage can break pose tracking itself, independent of the camera-angle problem.** On `my_sprint.mp4` the tracked landmark was observed jumping to background clutter in places. Any future ground-truth clip selection should check tracking confidence, not just camera geometry, before use.
- **Left vs. right leg-split asymmetry is unexplained.** In `stride_velocity_bridge.py` work, left-side same-frame leg-split values trended suspiciously near zero compared to a clean, sustained right-side signal. Could be a real gait asymmetry in the specific athlete filmed, or a timing/detection quirk specific to left-side contact events. Not root-caused.
- **`detect_sprint_phases` can't represent a "settled at new pace" scenario** — see bug #6's residual limitation above.
- **Job queue is in-memory and single-process.** State is lost on restart; will not work correctly across multiple server worker processes (requests could round-robin to a process that never ran the job). Needs a Redis/DB-backed store or a real task queue (Celery/RQ) before scaling beyond one process.
- **MediaPipe fallback is not automatic.** If the RTMPose worker is down, `/api/analyze/video` jobs fail with a clear error; nothing currently switches to the MediaPipe path automatically.
- **`app/services/pose_adapters/` is dead code.** `RTMPoseAdapter` + `registry.py` are never imported by any live or CLI code path, and its expected input format (raw MMPose-style `keypoints` list + parallel `keypoint_scores` list) doesn't match what the actual worker returns (a dict keyed by joint name, already normalized). If someone wires this up later expecting it to work like the rest of the pipeline, it will silently misbehave. Flagged, never fixed or removed.
- **Only sprint has been validated.** Hurdles/long jump/high jump code exists but has never touched real footage.
- **`backend/app/services/{digital_twin,digital_twin_v2,physics,fusion,motion,coach,talent,validation,research,readiness,athlete_intelligence,feature_store,pipeline}/`** — substantial code, zero validation this session. Unknown state.
- **`reports/coach.py`, `reports/scoring.py`, `reports/recommendations.py`** are empty 1-line stub files.
- **Database schema is not version-controlled** beyond one table (`digital_twin_v2/supabase_schema.sql`). See §5.
- ~~Frontend routing is broken in several places~~ **Fixed in §17.5.** All routes now resolve (real pages or honest `ComingSoon` placeholders); 404 fallback added; anchor links fixed.
- ~~Frontend is not connected to the backend at all~~ **Fixed in §17.1.** Full upload → analysis → report flow now works end-to-end via a signed-URL submission architecture. See §17.
- **`backend/requirements.txt` is UTF-16 encoded** (unusual; works with `pip install -r` but reads oddly with plain text tools — use `iconv -f UTF-16 -t UTF-8` to view it normally).
- **No authentication, rate limiting, or file-size limits** on either `/api/analyze/video` endpoint (file-upload or signed-URL variant, §17.1). The signed-URL variant does have SSRF mitigation (host/path/scheme allowlist, §17.1) but that's a different concern from auth - see §17.7 for the current isolation model and its limits.

---

## 12. Benchmark results (real clips tested this session)

Three real test clips live in `backend/examples/` (gitignored — not in git, only on this machine):

| Clip | Description | FPS/res/duration | Key findings |
|---|---|---|---|
| `my_sprint.mp4` | Archival B&W footage, crouching-start scene, stock (Pond5 watermark) | low quality | Tracking worked (94.4% observed); low knee/hip angle coverage in 2 of 3 segments due to degraded footage; low camera-angle problem also present (headroom ~32-41%) |
| `my_sprint_2.mp4` | Modern colour clip, "lower side corner view" camera (low, close, oblique), stock (Pond5 watermark) | 960x540, 50fps, 15.7s | 100% tracking coverage. After fixes: cadence 187.5 steps/min (46 events), ground contacts 46 (matching), stride frequency 1.56/s, duty factor 23.5% — all internally consistent. **This is the clip that exposed the ground-contact swing-vs-stance bug and the camera-height quality-gate blind spot.** Headroom ~40.4% (bad). |
| `my_sprint_3.mp4` | Modern colour clip, proper side-on waist-height camera, stock (Pond5 watermark) | 304x540, 24fps, 12.08s | 100% tracking coverage, 100% detection rate. Headroom ~19.2% (good — `camera_height_score: 100`). 3 of 6 visually-checked contact samples were clearly correct ground contact (vs. 0 of 9 on clip 2) — the decisive evidence for the camera-angle hypothesis. Still fails `biomechanics_ready` for a different, legitimate reason: ankle/feet visibility below threshold (likely the narrow 304px portrait framing clipping feet at times). |

All three clips are **licensed stock footage** (Pond5 watermarks visible) — not real user-captured content. Worth keeping in mind: real uploads from actual athletes may look different again (better or worse) than any of these.

Live end-to-end server test (this session, `b6b75cf`): `POST /api/analyze/video` with `my_sprint_3.mp4` returned in 84ms; job completed ~12s later (worker was GPU-warm) with `provider: rtmpose`, 290/290 frames tracked, 100% detection rate, `camera_height_score: 100.0`, correctly gated `biomechanics: skipped` for ankle/feet visibility — matching the CLI-based findings above exactly.

Test suite: **294 tests passing**, `pytest` from `backend/` with no arguments needed.

---

## 13. Remaining roadmap

Original 20-step roadmap phases (as stated by the product owner), annotated with status:

- **Step 1 (Validate biomechanics layer)** — mostly done for sprint: cadence/contact/phase-detection fixed and cross-validated. Ground-contact timing accuracy still open (§10/§11).
- **Step 2 (Sprint phase detection)** — built and improved this session (camera-robust signal), but the phase-boundary model has a known limitation (§9 bug #6, §11).
- **Steps 3-6 (Contact detection, stride metrics, joint metrics, symmetry)** — partially exist already in `biomechanics/` and `sprint/stride_geometry_engine.py`; contact detection specifically still unreliable.
- **Steps 7-9 (AI coach feedback, sprint score, elite comparison)** — not started. `reports/coach.py`/`scoring.py`/`recommendations.py` are empty stubs. **Elite comparison specifically flagged as needing real licensed reference data before attempting — a claims/liability risk, not just an engineering task.** When sprint score (step 8) is picked up: the `analysis_reports` table already exists for this exact purpose (`performance_score`, `confidence`, `analysis` jsonb) - see §5's "Architectural decision" writeup before building a new storage mechanism.
- **Steps 10-12 (Multi-camera, camera quality, auto-cropping)** — camera quality gating substantially improved this session (rotation + height/tilt); multi-camera and auto-cropping not started.
- **Step 13-15 (Digital twin, performance history, injury prediction)** — `digital_twin`/`digital_twin_v2` code exists, unvalidated. **Injury prediction flagged as needing real rigor before attempting — same class of risk as elite comparison, arguably higher given it's health-adjacent.**
- **Step 16-17 (Background processing, job queue)** — done this session (in-memory MVP version; needs upgrading before multi-process scale, see §11).
- **Step 18 (Video report: annotated video, graphs, PDF, AI explanation)** — not started beyond the text/JSON report.
- **Step 19 (Frontend integration)** — not started. This is a real, sizeable gap (§2/§3/§11).
- **Step 20 (Branding as "Shakti Motion Intelligence™")** — partially already true: the FastAPI app is titled `"Shakti Motion Intelligence API"` in `main.py`.

**Additional recommendations on record from this session** (not part of the original 20 steps):
- Ground-truth validation against real footage is the actual credibility differentiator for this product — worth continuing to invest in, not a one-off exercise.
- Design for real Indian filming conditions (phone cameras, imperfect angles) rather than lab-quality assumptions — directly motivated the camera-height gate.
- Coach/scout-side tooling (search, comparison, leaderboards) is currently completely absent despite being half the stated business model — worth its own workstream.
- Regional-language support for coaching feedback/UI — not started, not evaluated.
- Cost/throughput planning for RTMPose at scale — GPU inference cost per video will matter once there's real upload volume; not modeled yet.

---

## 14. Git history — major milestones

All on branch `main`, in `D:\shaktisportsai` (not the review worktree). Chronological, oldest first:

```
8d5f5fe  Convert project to monorepo architecture
e3db558  Build premium Shakti Sports AI homepage MVP
36ce7f1  Polish homepage structure and remove unused sections
b084093  Add auth onboarding and athlete console foundation
d6c4d92  Implement complete athlete performance upload workflow
ddd8fb7  feat: add FastAPI backend and AI video ingestion pipeline
fbe057a  feat: add RTMPose biomechanics pipeline for sprint analysis          <- huge commit, all the RTMPose/biomechanics work that had been sitting uncommitted
7927c86  fix: stop discarding real motion data in knee-cycle/cadence detection    (bug #3)
bc1d77d  feat: add per-segment sprint biomechanics report                     (§4.6)
65d0877  fix: ground-contact detection was undercounting by ~3x               (bug #4)
3866291  feat: camera-motion-robust velocity signal for sprint phase detection (bug #6)
c5db7ab  docs: flag ground-contact detection as confirmed unreliable for low camera angles  (§10)
bb62af0  docs: quantify ground-contact detection error against manual ground truth  (§10)
a0c6676  docs: camera angle, not the detection algorithm, looks like the real variable  (§10)
0311c74  feat: add camera-height quality check, closing the blind spot we found  (bug #7)
51ad8aa  feat: make video analysis async, so long analyses don't block the request  (bug #8)
b6b75cf  feat: wire RTMPose into the live API                                 (bug #9)
c72641a  docs: add engineering handoff document
6089684  fix: rule out ground-contact threshold calibration with quantified proof  (§10.1)
80b9a2e  feat: wire performance uploads to the FastAPI analysis backend and render real reports  (§17.1)
f78e724  feat: submit analysis via signed storage URL, harden the job lifecycle  (§17.1/§17.2)
c8a932c  fix: self-heal stuck analyzing rows and explain skip reasons on the detail page  (§17.2)
d16f506  fix: wire up dead athlete nav links and add a 404 fallback              (§17.5)
15908f2  fix: close RLS gap allowing silent athlete_id reassignment on performances  (§17.3)
2721bc5  feat: build real coach and academy onboarding, closing a sign-up dead-end  (§17.4)
ca4b9ed  docs: document the analysis_reports vs performances.analysis_result decision  (§17.3)
b4df82c  fix: route sign-in and home redirects by role instead of always to athlete console  (§17.4)
d8f4366  feat: add real About and Mission pages, finish wiring the footer      (§17.5/§17.6)
2cde8b5  feat: add real contact form with a Supabase backstop                  (§17.6) <- HEAD, current tip
```

All commits are pushed to `origin/main` (`https://github.com/dsaikat1991/shakti-sports-ai.git`).

---

## 15. Environment requirements

- **OS**: Windows (this has been developed/tested on Windows 11 with Git Bash / PowerShell available).
- **GPU**: NVIDIA GPU with CUDA 12.1 support required for the RTMPose worker. Tested on a GTX 1650 (4GB VRAM) — modest but sufficient for `rtmpose-t` (tiny model).
- **Two separate Python environments in `backend/`**:
  - `.venv` — Python 3.14.6. Has `fastapi`, `mediapipe`, `opencv-python`, `pytest`, etc. (see `requirements.txt`). Used for: running the main API server, running `pytest`. Does **not** have torch/mmpose/mmdet.
  - `.venv-rtmpose` — Python 3.11.9 (older, required for mmpose/mmdet compatibility). Has `torch==2.1.2+cu121`, `mmpose==1.3.2`, `mmdet==3.2.0`, plus `requirements-worker-extra.txt` and `rtmpose-constraints.txt` pins. Used **only** to run `rtmpose_worker` and the CLI scripts in `scripts/`.
- **Node**: v24.13.1 / npm 11.10.0 (frontend).
- **To run the full stack locally**:
  1. `cd backend && ./.venv-rtmpose/Scripts/python.exe -m uvicorn rtmpose_worker.app:app --port 8011` — start the GPU worker. Wait for `/health` to show `"initialized": true` (first `/initialize` call triggers model download/load, takes a while cold).
  2. `cd backend && ./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000` — start the main API.
  3. `cd frontend && npm run dev` — start the frontend (Vite, default port 5173 - **must stay 5173**, backend CORS hardcodes it). **As of §17, all three services (worker, main API, frontend) are needed together for the frontend's analysis flow to actually work**, not just for manual `curl` testing as this line originally said.
  4. To run tests: `cd backend && ./.venv/Scripts/python.exe -m pytest` (no args needed — `pytest.ini` scopes collection correctly). Frontend: `cd frontend && npm run test` (Vitest, 23 tests, added §17) and `npx tsc -b`.
- **Environment variables**:
  - `backend/.env.rtmpose-live.example` documents the worker's own config: `RTMPOSE_MODEL`, `RTMPOSE_DEVICE` (default `cuda:0`), `RTMPOSE_SCHEMA` (`halpe26`), `RTMPOSE_MIN_CONFIDENCE` (`0.35`), `RTMPOSE_MAX_PEOPLE` (`4`), optional `RTMPOSE_DET_MODEL`.
  - `RTMPOSE_WORKER_URL` (in `live_analyzer.py`) — base URL the main backend uses to reach the worker, default `http://127.0.0.1:8011`.
  - `frontend/.env.local` — `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_BASE_URL` (new, §17.8, default `http://localhost:8000`).
  - No `.env.example` exists for the main backend's own config (CORS origin, temp dir, etc. are currently hardcoded in `main.py`/`routes.py`, not env-driven).

---

## 16. Exact next task (historical - Option A below was picked up; see §17 for what actually happened and the current next task)

**Option B (ground-contact detection) was picked up in a follow-up session** (§10.1) — but "properly calibrate a heuristic" turned out to be ruled out by the data itself (direct overlap counterexample, §10.1), and labeling more clips surfaced confounds (occlusion, tracking reliability) that limited how much clean new ground truth could actually be produced from the 3 existing example clips alone. The honest state now: `contact_time_ms`/`flight_time`/`duty_factor` are still not trustworthy, and the path forward needs either (a) real new footage — the 3 existing Pond5 stock clips are close to exhausted as a labeling source, screened first for occlusion/tracking-confidence per §10.1's recommendation — or (b) a richer feature set / different technical approach than single-signal foot height, since calibrating that one signal is now proven not to work.

**Option A — Frontend integration (Step 19) — still not started.** This remains the single biggest gap between "backend works" and "product works," and is now the more clearly actionable option: pure engineering work with everything needed already in the repo, versus Option B which is now blocked on real footage or a harder algorithmic pivot. Wire the frontend's performance-upload flow to actually call `/api/analyze/video` and poll for results, instead of only writing to Supabase. Requires: an HTTP client call in `performance.service.ts` (or a new service file) to submit the uploaded video to the backend after/instead of the Supabase storage upload, a polling mechanism (the `PerformanceProcessing.tsx` page already exists as a likely home for this), and a decision about where the analysis result gets stored (write back to Supabase `performances` table? A new table?). Also fix the known broken routes while touching this area (§11).

**Recommendation**: Option A. Closing it turns this from "a validated backend" into "a working product" that could start generating the real user footage that Option B's next step (new labeled clips) actually needs — the two options are complementary, not competing, and A now unblocks B rather than the reverse.

If picking up ground-contact work again instead: do not re-attempt foot-height threshold tuning (ruled out, §10.1); either source new real footage (screened for occlusion/tracking-confidence first) or explore a richer feature set / different approach; `scripts/label_contact_frames.py` (frame-scrubbing labeling tool) already exists and should be reused rather than rebuilt.

Whichever is chosen: run `cd backend && ./.venv/Scripts/python.exe -m pytest` first to confirm the starting state is clean (294 passing), and re-read §11 in full before writing any code — several of those limitations are easy to accidentally reintroduce or build on top of without realizing it.

---

## 17. Session update: frontend integration, RLS hardening, navigation, marketing pages

Everything below happened across one long follow-up session, commits `80b9a2e` through `2cde8b5` (11 commits, all pushed to `origin/main`). Option A (§16) was picked up, finished, and then extended well past its original scope as real gaps kept surfacing during verification. **This section is the authoritative current state — treat §1-§16 as historical/backend-depth reference, not current frontend status.**

### 17.1 Frontend ↔ backend integration is real now

The frontend no longer only talks to Supabase. Full flow:

1. Athlete uploads a video in the wizard → uploaded to Supabase Storage (`performance-recordings` bucket, private) → a `performances` row is created (`upload_status: "uploaded"`).
2. The browser mints a **short-lived Supabase Storage signed URL** for that just-uploaded object (`supabase.storage.from(...).createSignedUrl(...)`) and submits it to a **new backend endpoint**, `POST /api/analyze/video-url` (JSON body `{"video_url": "..."}`), instead of re-uploading the raw file a second time.
3. FastAPI downloads the video itself via that signed URL (`httpx`, already a dependency) and runs the exact same background job pipeline as the original file-upload endpoint (`POST /api/analyze/video`, still present and unchanged — used for direct multipart uploads; `/analyze/video-url` is used for the browser's signed-URL path and for **retry**, since retry doesn't have the original `File` object in memory).
4. `analysis_job_id` is written onto the `performances` row (migration `0002`), and the frontend polls `GET /api/analyze/video/{job_id}` (bounded: stops on completion/failure/unmount/10-minute timeout) and persists the terminal result into `performances.analysis_result`/`analysis_error` (also migration `0002`).
5. `PerformanceDetail.tsx` renders the real result: detection rate, recording-quality metrics, and — if biomechanics wasn't skipped — the full per-segment report (cadence, stride, ground contact, joint angles, limitations).

**Why signed URL instead of just re-uploading from the browser**: confirmed this session that the athlete's own Storage RLS already permits minting a signed URL for their own uploaded object with zero policy changes. This avoids double-uploading the same video from the client, and — critically — makes retry possible from a page that doesn't have the original file (performance history, a reloaded detail page), which raw re-upload structurally cannot support.

**SSRF**: `POST /api/analyze/video-url` fetches a client-supplied URL server-side, a classic SSRF vector if unconstrained. Mitigated with a strict host+path+scheme allowlist checked before any network call — see `backend/app/api/routes.py` and `docs/ANALYSIS_WORKFLOW_AUDIT.md` §4 for the full mitigation list.

**Full detail, including the audit that was done *before* writing any code**: `docs/ANALYSIS_WORKFLOW_AUDIT.md`.

### 17.2 Bugs found while wiring this up (all fixed)

- **`performances.upload_status` CHECK constraint doesn't include `"processing"`** — only `draft`/`uploaded`/`analyzing`/`completed`/`failed`. First-pass code wrote `"processing"` and failed silently (Supabase update returned an error that was never checked). Fixed by using `"analyzing"` for the in-flight state and adding error logging to every Supabase write in this flow so a future silent failure like this would actually surface.
- **Only the processing page polled for job completion.** Navigating away before a job finished (e.g. straight to the dashboard) left the row permanently stuck on `"analyzing"` even after the backend genuinely completed the job — confirmed live with a real stuck user upload. Fixed by also polling from `PerformanceDetail.tsx` whenever it loads a still-`analyzing` performance, so simply revisiting a performance's detail page self-heals it.
- **`joint_angles` in the biomechanics result is an object keyed by joint name** (`{left_knee: {...}, right_knee: {...}, ...}`), not an array — first-pass rendering code assumed an array and would have silently hidden the whole joint-angle table for real data.
- **Postgres `jsonb` does not preserve object key insertion order** — it re-serializes keys sorted by (length, then alphabetically). Confirmed by reproducing the exact scrambled key order Postgres actually returns. This meant `joint_angles`' row order in the UI was arbitrary on every read, regardless of what order the backend produced. Fixed by sorting to an explicit canonical order client-side (`JOINT_ANGLE_ORDER` in `PerformanceDetail.tsx`) rather than trusting object key order from any jsonb column, anywhere.
- **`performances.athlete_id` foreign keys to `athlete_profiles`, not `profiles` directly** (discovered via full schema introspection, §5) — a coach/academy account structurally cannot have `performances` rows, which matters for §17.4 below.

### 17.3 RLS hardening

Full schema (all tables, columns, RLS policies, check constraints, storage bucket config) is now **confirmed via direct introspection**, not inferred from frontend code — see the updated §5 above and `docs/ANALYSIS_WORKFLOW_AUDIT.md`.

- **`performances` UPDATE policy had no `WITH CHECK`** — `USING (auth.uid() = athlete_id)` correctly restricted which rows could be targeted, but nothing restricted what a row could become afterward. An authenticated athlete could reassign their own row to a different `athlete_id`, silently orphaning it from their own view. Fixed (migration `0003`), verified live: the exact exploit (`PATCH` a row's `athlete_id` to a different UUID) now returns `403`, confirmed unchanged before/after via direct API calls.
- **`analysis_reports` table exists, unused, reserved for a future feature** — see §5's "Architectural decision" writeup. Deliberately left alone; do not migrate the current raw job result into it or invent placeholder scores to populate it.
- **`contact_submissions` table added** (migration `0004`) as a backstop for the new `/contact` form — public `INSERT` (the page is unauthenticated-accessible), no `SELECT` for anon/authenticated (only the project owner via the Supabase dashboard can read submissions). Verified both directions live: an anonymous insert succeeds, and the same anonymous client reading the table back gets an empty result despite rows existing.

### 17.4 Coach/academy: sign-up, onboarding, and routing are now real

Previously, `ChooseRole.tsx` already routed new coach/academy sign-ups to `/onboarding/coach` and `/onboarding/academy` — but neither route existed, and `CoachOnboarding.tsx`/`AcademyOnboarding.tsx` were empty stub files, so both rendered a blank page. Separately, **every sign-in and every logged-in visit to `/` was hardcoded to redirect to `/console/athlete`**, regardless of role.

Fixed:
- Real onboarding forms built for both roles, writing to `coach_profiles`/`academy_profiles` — both tables **already existed in Supabase with correct RLS**, just unused; no new migration was needed for this part, only wiring.
- `AuthContext` now fetches and exposes `role`/`roleLoading` (from `profiles.role`) alongside the Supabase session.
- Sign-in and the logged-in `/` redirect are now role-aware (`roleHomeRoute()` in `constants/routes.ts`): athlete → `/console/athlete`, coach → `/console/coach`, academy → `/console/academy`.
- `/console/coach` and `/console/academy` now exist, landing on a shared `PendingConsole` holding screen (no real console for either role exists yet — this only stops the athlete-console leak, it doesn't build coach/academy functionality).
- `RoleGate` (new route guard) blocks **direct URL navigation** into `/console/athlete/*` for a signed-in coach/academy account too, not just the login-time redirect. `role === null` (authenticated but mid-onboarding, no `profiles` row yet) is treated as pass-through, not blocked.

**Not done**: real coach/academy consoles (talent search, squad management, etc.) — `PendingConsole` is an honest "coming soon," not a feature.

### 17.5 Navigation/routing cleanup

Found via a full static sweep (every `Link`/`href`/`navigate` call cross-referenced against the actual route table) plus live verification of the worst ones:

- 5 of 7 athlete sidebar links (Reports/Progress/Discover/Profile/Settings) pointed at routes that didn't exist → blank page. Now resolve to `ComingSoon` placeholders (honest "not built yet," not fabricated functionality).
- No catch-all/404 route existed anywhere → any bad URL rendered a silent blank page. Added `NotFound`.
- Duplicate `id="platform"` on two different homepage sections (invalid HTML, one was unreachable via anchor) → renamed one to `id="how-it-works"`.
- Marketing nav's "About" anchor (`#about`) had no matching element anywhere → removed (nothing to point it at at the time; now real, see §17.6).
- All 9 footer links were literal `href="#"` placeholders → now: About/Mission/Contact link to real pages (§17.6); "How it works"/"For athletes"/"For coaches" link to their real existing homepage sections; "AI analysis"/"Recording guide"/"For academies" get honest `ComingSoon` placeholders (no matching content exists yet for these three — did not fabricate anchors or pages for them).

### 17.6 New marketing pages

- **`/about`, `/mission`** — real content, provided directly by the project owner, published as-is.
- **`/contact`** — real form (name/email/subject/message). Submits to the `contact_submissions` backstop (§17.3) first, then opens a `mailto:contact@shaktisportsai.com` link pre-filled with the message. Verified end-to-end by intercepting the actual `fetch` call from a real form submission, not just a synthetic test.
- **`/terms`, `/privacy`** — deliberately **not** drafted with real legal text. This product collects real personal data including from apparent minors (the marketing copy's own athlete examples show ages 16-17), so these carry real legal weight and need actual legal input, not AI-generated boilerplate. Currently `ComingSoon` placeholders. **Do not fill these in without real reviewed text from the project owner or counsel.**

### 17.7 What's actually left open now

- **Terms of Use / Privacy Policy real content** — blocked on the project owner providing reviewed text (§17.6). Given the apparent-minors data collection, this is worth prioritizing before more real signups happen, not just a nice-to-have.
- **Footer "AI analysis" / "Recording guide" / "For academies"** — still `ComingSoon` placeholders with no real destination.
- **Real coach/academy consoles** — `PendingConsole` only; no actual talent-search/squad-management functionality exists.
- **Backend still has no authentication layer of its own** (pre-existing, §6/§11). Isolation for the signed-URL flow relies on Supabase RLS (only the owning athlete can mint a signed URL for their own video) + unguessable job IDs, not backend-level auth. A determined attacker who obtained someone else's `job_id` could poll its status with no ownership check. Not fixed this session; flagged, not urgent given no other realistic path to obtain a stray `job_id` exists today.
- **Job queue is still in-memory, single-process** (§11) — unrelated to this session's work, still an open scaling gap.
- **Ground-contact/duty-factor accuracy** (§10/§10.1/§16 Option B) — untouched this session, still blocked on real new footage or a richer feature set.
- **Server-initiated job reconciliation** — the self-heal fix in §17.2 makes polling more resilient, but it's still fundamentally client-driven; if a user never revisits any page for a stuck performance, it stays stuck indefinitely. A real fix would be push-based (a webhook/callback from the backend into Supabase on job completion), not attempted this session.

### 17.8 Environment additions

- `frontend/.env.local` gained `VITE_API_BASE_URL` (default `http://localhost:8000`) — the frontend's base URL for the FastAPI backend.
- To run the full stack now meaningfully exercises all three services together (§15's steps 1-3 are all required for the frontend's analysis flow to work, not just for manual `curl` testing as previously written).
- `.claude/launch.json` added — lets the frontend dev server be started via the preview tooling (`name: "frontend"`, port 5173 - **must stay 5173**, the backend's CORS config in `main.py` hardcodes `http://localhost:5173`).

### 17.9 Exact next task (historical - "real coach/academy consoles" was picked up; see §18 for what actually happened and the current next task)

No single obvious next step was chosen at the end of this session - the work above was a chain of "fix this, which surfaces that" rather than a planned roadmap item, and it ran out naturally rather than hitting a real stopping point. Pick based on what's actually wanted next:

- **Fastest, lowest-risk**: Terms of Use / Privacy Policy real content (§17.6/§17.7) - purely a content/legal task, zero engineering risk, but blocked on the project owner (or counsel) providing real text. Worth raising proactively given the apparent-minors data collection.
- **Product-shaping decision needed first**: real coach/academy consoles (§17.4) - talent search, squad management. This is a substantial new feature area, not a quick fix; needs its own scoping conversation before any code, the same way Option A did back in §16.
- **Reopens a previously-shelved, harder problem**: ground-contact detection (§10/§10.1/§16 Option B) - still blocked on real new footage or a fundamentally different technical approach; do not re-attempt threshold tuning, that's proven not to work.
- **Infrastructure, not user-facing**: job queue durability (in-memory, single-process, §11) or backend authentication (§17.7) - real gaps, but nothing is currently broken by them; worth doing before this scales past one process or gets meaningfully more usage, not urgent today.

Whichever is picked: run `cd backend && ./.venv/Scripts/python.exe -m pytest` (294 passing) and `cd frontend && npm run test` (23 passing) first to confirm a clean starting state, and skim §17 in full before writing code - several of the bugs in §17.2 (jsonb key ordering, the `upload_status` CHECK constraint values, the object-vs-array `joint_angles` shape) are exactly the kind of thing that's easy to reintroduce by anyone who hasn't hit them once already.

---

## 18. Session update: real coach/academy consoles (Phase 1 - connected-athlete roster)

Same session as §17, done as a separate follow-up piece of work. **This section is the authoritative current state for coach/academy functionality** - §17.4's "onboarding only, `PendingConsole` placeholder" description is now historical.

**Status as of writing: migrations `0005`/`0006` are applied to the real Supabase project, and the full connection lifecycle has been live-verified end-to-end in a real browser session with two real accounts (see §18.5) - not just automated checks.** ~~Code is not yet committed to git~~ **Update: committed in `40b884e`, confirmed via `git log` in the §22 session - this note was stale by the time it was next read.**

### 18.1 What this is

Coach and academy accounts previously landed on an identical `PendingConsole` placeholder after onboarding - no real functionality existed for either role, and no table anywhere linked a coach/academy account to an athlete account (confirmed via audit before any code was written: every RLS policy on `profiles`/`athlete_profiles`/`performances` was `auth.uid() = <owner>` only). This phase builds the connection layer plus a minimal console on top of it:

- A coach or academy can invite a specific athlete by email; an athlete can equally invite a specific coach/academy by email. Either direction goes through the same `request_partner_connection(target_email)` Postgres RPC (`SECURITY DEFINER`) - the only way a connection row can be created, precisely because neither party has RLS visibility into the other's `profiles` row before a connection exists, so a plain client-side lookup-then-insert isn't possible.
- The recipient accepts or rejects. Only on **acceptance** does the coach/academy gain `SELECT` access to that athlete's `athlete_profiles` row and `performances` rows (including `analysis_result` - not raw video, that's deferred, see §18.3). A **pending** request only exposes basic name/org info, and only to the request's *recipient*, not the sender (see §18.2 for why this is directional, not symmetric).
- Either party can revoke an accepted connection at any time, which immediately removes the coach/academy's access (the RLS policies check `status = 'accepted'` live, not a point-in-time grant).
- A coach/academy can attach private notes to a connected athlete, visible only to the note's author, never the athlete.

### 18.2 Data model and RLS (the real substance of this change)

Two new migrations, written but **not yet run** - same hand-run-in-the-Supabase-SQL-editor workflow as every prior migration in this repo:

- `supabase/migrations/0005_add_coach_athlete_connections.sql` - the `coach_athlete_connections` table, the `request_partner_connection()` RPC, a `BEFORE UPDATE` trigger that owns the connection's entire state machine, and five new *additive* RLS policies on `profiles`/`coach_profiles`/`academy_profiles`/`athlete_profiles`/`performances`. Nothing existing is touched or weakened.
- `supabase/migrations/0006_add_coach_athlete_notes.sql` - the `coach_athlete_notes` table (private, author-only).

This design went through an explicit adversarial review pass (a second planning agent instructed to find holes) before being written, which caught two real problems in the first draft, both fixed in the shipped SQL:

1. **An information-disclosure leak.** The first draft made pending-request profile visibility *symmetric* (both parties see each other's `profiles` row while pending). Combined with `request_partner_connection()`'s "generic exception either way" design, that would have turned the RPC into a two-step name-enumeration oracle: call it with a guessed email to confirm a registered athlete account exists, then read their real name straight off the now-visible pending row. Fixed by making visibility **directional** - only the *recipient* of a still-pending request can see the *initiator's* base profile, never the reverse.
2. **A Postgres RLS multi-policy combination bug.** The first draft used two separate `UPDATE` policies (one for "respond to a request", one for "revoke an accepted connection"). Postgres combines multiple permissive policies' `USING` clauses with OR and their `WITH CHECK` clauses with OR *independently*, not as matched pairs - which would have let a recipient of a still-pending request jump straight to `status = 'revoked'` by satisfying one policy's `USING` and a different policy's `WITH CHECK`. Fixed by collapsing to one broad row-access `UPDATE` policy plus a trigger (`enforce_coach_athlete_connection_transition()`) that owns the entire legal-transition state machine (`pending → accepted/rejected` only by the non-initiating party, `accepted → revoked` by either party, `rejected/revoked → pending` reactivation gated behind a transaction-local flag that only `request_partner_connection()` sets, so a raw client `UPDATE` can't reactivate a stale connection while bypassing the RPC's email/role validation).

Other things worth knowing about the shipped design:
- `coach_id`/`athlete_id` are immutable post-insert (trigger-enforced - `WITH CHECK` alone can only see the new row, not old-vs-new, so a trigger is the only place this can actually be enforced).
- There is deliberately **no direct `INSERT` policy** on `coach_athlete_connections` - `request_partner_connection()` is the sole creation path, avoiding a second, independently-maintained copy of the same authorization logic.
- `invited_email` is stored on the connection row (set by the RPC from the email the inviter actually typed) purely so the *inviter's own* "sent invitations" list can show who they invited, given they have no other way to see the recipient's profile before acceptance. This isn't a new disclosure - the inviter already knows the email, and a recipient seeing their own email echoed back is not a leak either.
- **Known, accepted gaps, flagged not solved**: no rate limiting on `request_partner_connection` (nothing in this app has rate limiting anywhere - see §11/§17.7); acceptance is not gated on `coach_profiles.verified`/`academy_profiles.verified` (those columns exist but stay unused this phase - gating on them would lock out every existing account, and a full verification workflow is explicitly out of scope, see §18.3). The athlete's own accept action is the trust boundary for this phase.

### 18.3 Explicitly deferred (per the product owner's own phasing)

Nationwide discovery/search UI, a distilled "Performance Index"/AI-potential score, a full coach/academy verification workflow, an `organizations`/multi-tenant model, guardian-consent records for minors, messaging, automatic recommendations, raw video playback access for coaches (analysis results/metrics only this phase), and an athlete-visible "coaching feedback" channel (only private, author-only coach notes shipped). None of these require a destructive schema change later - `partner_role` already distinguishes coach vs. academy without a join (for a future organizations model), `accepted` status is already the single choke point for all athlete-data visibility (a future `guardian_consent_at` column is a one-column, one-predicate addition), and `verified` columns already exist on `coach_profiles`/`academy_profiles` for a future verification tier.

### 18.4 Frontend

New `frontend/src/features/partners/` feature folder (coach and academy share one implementation - `PartnerLayout`, `PartnerHome`, `PartnerRoster`, `PartnerAthleteDetail`, `PartnerRequests` - role-driven copy only, not two parallel folders), plus `frontend/src/features/athlete/pages/AthleteCoaches.tsx` (new "Coaches" nav item in `AthleteLayout`) for the athlete's own side of accept/reject/revoke/invite. `AppRouter.tsx`'s `/console/coach` and `/console/academy` routes now mount `PartnerLayout` with real nested routes instead of the old `PendingConsole` placeholder, which has been deleted (it had zero remaining usages after this change). `PartnerAthleteDetail.tsx` reuses the existing `AnalysisReport` component from `performances/pages/PerformanceDetail.tsx` as-is (a pure presentational export with no athlete-only actions like retry) rather than reusing the whole `PerformanceDetail` page, which has retry/processing-link UI that would silently fail under a coach's RLS grant (SELECT-only, no UPDATE access to `performances`).

Also fixed in passing: `UserMenu.tsx`'s "Dashboard" link was hardcoded to `ROUTES.ATHLETE.HOME` - harmless while only `AthleteLayout` used it, but would have sent a coach/academy user on a pointless detour through a `RoleGate` bounce. Now uses `roleHomeRoute(role)`. `CoachOnboarding.tsx`/`AcademyOnboarding.tsx`'s step-4 completion screen also predated this work - it only offered "Sign Out" and its copy claimed the console was "still being built" (true when it was written, stale the moment this session made it real). Both now navigate to the real console (`ROUTES.COACH.HOME`/`ROUTES.ACADEMY.HOME`) with updated copy. Caught live while walking through the actual sign-up flow during verification, not by code review - a reminder that onboarding completion screens are easy to leave stale when the thing they're gating gets built later.

New pure helper `frontend/src/features/partners/lib/getConnectionViewState.ts` (unit-tested, 7 cases) resolves what a connection row means from the current viewer's perspective (`outgoing_request` / `incoming_request` / `connected` / `declined` / `ended`) - used by both `PartnerRequests.tsx` and `AthleteCoaches.tsx` so both sides of the same table stay in sync without duplicating the perspective logic.

### 18.5 Verification performed

Automated:
- `cd backend && ./.venv/Scripts/python.exe -m pytest` - 302 passed, confirmed untouched (this work doesn't touch `backend/` at all).
- `cd frontend && npm run test` - 30 passed (23 existing + 7 new `getConnectionViewState` cases).
- `npx tsc -b --force` - clean, no errors.

**Live, both migrations applied to the real Supabase project** (project owner ran `0005` then `0006` in the SQL editor - `0005` initially hit `ERROR: 42601: unterminated dollar-quoted string`, which turned out to be a paste that got truncated partway through the SQL editor, not a bug in the migration itself; re-copying the full file resolved it). Full walkthrough done in a real browser session against the live app with two freshly-created real accounts (`shakti.qa.athlete@example.com` / `shakti.qa.coach@example.com`, both still in Supabase - fine to leave or delete):

1. Signed up and onboarded both a real athlete account and a real coach account through the actual sign-up/onboarding flow (this is what caught the stale onboarding-CTA bug noted in §18.4).
2. Coach sent an invite to the athlete's email from `/console/coach/requests` - `request_partner_connection()` RPC succeeded, row created with `status = 'pending'`, `initiated_by = 'coach'`.
3. **Confirmed the directional pending-visibility fix works as designed**: on the coach's side, the pending row rendered with no athlete profile data (fell back to `invited_email`, exactly as intended - the coach-as-initiator has no profile visibility yet). On the athlete's side (`/console/athlete/coaches`), the same pending row showed the coach's real name/email/role in full - the recipient can see the initiator, not the reverse.
4. Athlete clicked Accept. Status flipped `pending -> accepted` (the trigger's state-machine, exercised for real for the first time - non-initiator responding to a pending request).
5. **Confirmed accepted-only data unlock**: coach's roster (`/console/coach/athletes`) now showed the athlete's real name/email; opening the athlete detail page showed the real `athlete_profiles` data (preferred event: Sprint, from onboarding) and an honest "hasn't uploaded any performances yet" at this point in the walkthrough (see the follow-up pass below for the populated case).
6. **Confirmed private notes work**: added a note as the coach ("Strong start technique, needs work on top-end speed."), it saved and rendered immediately. No athlete-facing UI exists to see it (by construction - see §18.1), and the RLS policy (`auth.uid() = coach_id`) is the actual enforcement boundary regardless.
7. Athlete clicked Revoke Access. Status flipped `accepted -> revoked`.
8. **Confirmed revocation actually removes access live**: athlete's connected-coaches list went back to "No coaches yet"; coach's roster independently went back to "No connected athletes yet" on a fresh page load (not just optimistic UI - a real re-query against the DB, since `accepted`-only is a live predicate re-evaluated on every query, not a point-in-time grant).
9. Zero browser console errors and zero dev-server errors at any point across the whole walkthrough.

**Follow-up pass: populated performance report.** The Browser pane's automation can't drive a native file-picker, so the upload -> analyze -> persist pipeline was exercised by directly calling the same REST/API sequence the frontend itself makes (Supabase Auth password grant to get the athlete's real access token, `POST /storage/v1/object/...` for the video, `POST /rest/v1/performances` for the row, `POST /api/analyze/video` on the real FastAPI backend, poll `GET /api/analyze/video/{job_id}`, `PATCH` the row with the result) - a faithful reproduction of `useCreatePerformance`'s real sequence, not a shortcut around it. Found both the RTMPose worker (port 8011, GPU) and the main API (port 8000) already running and healthy from a prior session - didn't need to start either. Used `backend/examples/my_sprint_3.mp4` (the "good angle" benchmark clip from §12). Result matched the §12 benchmark exactly (100% detection, 12.1s, Side View, biomechanics correctly skipped for ankle/feet visibility at 68%/44%) - confirmed by rendering identically on the athlete's own `PerformanceDetail.tsx` first, then:

10. Reconnected the coach and athlete (the earlier pass had revoked the connection) by re-inviting through the RPC - **this also live-verified the `rejected/revoked -> pending` reactivation path** (gated behind the `app.connection_reactivation` session flag, previously only unit-tested) for the first time, live and unprompted, as a side effect of re-running the walkthrough.
11. **Confirmed the populated-report path end to end**: `PartnerAthleteDetail.tsx`'s "Performance History" showed the real completed performance instead of the empty state; expanding it rendered the exact same `AnalysisReport` output as the athlete's own page - detection rate, duration, camera view, the full biomechanics-readiness-checks table, and general recording-quality table, byte-for-byte identical data. **Confirmed no video element or video URL appears anywhere in the coach's view** - the Phase-1 design decision to withhold raw video from coaches (§18.1/§18.3) holds in practice, not just in the RLS policy.
12. The private note added in step 6 was still present and intact after the revoke/reactivate/re-accept cycle in between - confirms notes are tied to the connection row's identity, not to a particular `accepted` window, exactly as designed (§18.2's `coach_athlete_notes` note about author access surviving revocation).

**Not exercised, still open**: the athlete-initiated invite direction (only coach-initiated was tested live, though it's the same RPC/trigger code path with the roles swapped, and is covered by the `getConnectionViewState` unit tests for both directions), academy-role behavior specifically (coach and academy share 100% of the same code path - only the role label differs - so this is low-risk but not independently confirmed live), and reject (only accept and revoke were exercised).

The two seed accounts now each carry one real, fully-analyzed performance and an active connection between them - useful as persistent manual-test fixtures for whoever picks this up next, not just throwaway QA noise.

### 18.6 Exact next task (historical - ground-contact detection was picked up next, redirected into data-collection infrastructure rather than a direct fix; see §19)

This phase is done and verified, including the populated-report path. The project owner has explicitly deferred Terms/Privacy content until every other important platform aspect is done first - do not pick that up unprompted, despite it being flagged as time-sensitive in §17.6/§17.7. Pick between: ground-contact detection (§10/§10.1); job-queue/auth infrastructure (§11); or extend this phase - coach profile editing is still a `ComingSoon` stub, "coaching feedback" visible to the athlete (deferred in §18.3) is a natural fast-follow now that private notes exist as a base to build on, and the remaining not-exercised paths from §18.5 (reject, academy role specifically, athlete-initiated invites) are worth a pass before this is fully trusted at higher traffic.

---

## 19. Session update: sprint biomechanics research dataset infrastructure

Same overall session, a distinct follow-up piece of work. **Ground-contact detection itself was explicitly NOT touched.** The project owner directed that further engineering effort on the heuristic stop until a substantially larger, more diverse labeled dataset exists (real footage is being actively collected across different places/lighting as of this writing) - this section is the *infrastructure* for that collection-and-validation phase, not a fix.

### 19.1 What this is

A new `backend/datasets/sprint_biomechanics/` area plus three CLI tools (`backend/scripts/screen_clip.py` new, `label_contact_frames.py` extended, `benchmark_contact_detector.py` new) implementing a **screen → label → benchmark** workflow:

1. **Screen** (`screen_clip.py`) - runs the exact same tracking + quality-gate pipeline the production API uses (`live_analyzer.analyze_video()`, zero reimplemented logic) against a candidate clip and derives an `accept`/`marginal`/`reject` verdict that answers "is this clip *labelable*" (tracking reliable enough, foot visible enough), not "does it pass `biomechanics_ready`" - a bad-angle clip is `marginal`, not `reject`, because bad-angle footage is exactly what exposed the original bug and remains valuable to label.
2. **Label** (`label_contact_frames.py`, extended with `--emit-label-skeleton`) - the existing tile-review tool (already reuses the real `contact_events.py` detector to generate reviewable windows) now also writes/updates a structured `labels/<clip_id>.json` skeleton per window, so a reviewer fills in a verdict directly instead of hand-authoring JSON from scratch (part of why the old `tests/fixtures/ground_truth_contact_labels.json` ended up with two incompatible ad-hoc shapes over time - not touched or migrated by this work, left as historical reference).
3. **Benchmark** (`benchmark_contact_detector.py`, new) - runs the real, unmodified production detector against a labeled clip and computes precision/recall/F1/timing-error via `app.services.biomechanics.gait_event_evaluator`.

### 19.2 A significant discovery made while researching this: unused, already-correct evaluation infrastructure

`gait_event_evaluator.py` (`match_events`/`evaluate_events`/`evaluate_by_event_type`) and `gait_event_models.py` (`GaitEvent`/`EventMatch`) already exist, are already tested (`test_gait_event_evaluator.py`, `test_gait_detector_benchmark.py`), and already implement a complete, detector-agnostic precision/recall/F1/timing-error engine (greedy nearest-timestamp matching by event type + side, with a configurable tolerance). It was built for an unrelated, unused detector variant (`gait_event_detector_v3`) and had **never been connected to real ground truth or to the actively-used `contact_events.py` detector** - not mentioned anywhere in §10/§10.1/§11. `benchmark_contact_detector.py` is the first thing to actually wire it up to real data. Worth knowing this exists before anyone considers building new metrics-computation code for future detector evaluation - it's already here, generic, and correct.

### 19.3 Key design decision: one label primitive covers three research questions

`flight_time.py`'s `estimate_flight_times()`/`estimate_duty_factor()` both take `contact_events` as their only real input. So labeling ground-contact events well is the single thing that unlocks validation for ground-contact detection, flight-time estimation, *and* duty-factor - there's no separate labeling effort for each. See `backend/datasets/sprint_biomechanics/README.md` for the full reasoning.

### 19.4 Honest phasing - what this does NOT yet solve

V1 labels are **single-point** contact judgments (a representative timestamp per contact, matching the detector's own `peak_timestamp_ms`) - enough to validate detection accuracy (is/isn't there a contact, roughly when), but **not** enough to tightly validate flight-time/duty-factor, which need labeled contact **start and end** (a full stance interval). The schema (`label_sets` as a dict, not a flat list) is designed to accept a future `stance_interval` label set without a breaking change, but that labeling methodology doesn't exist yet. `benchmark_contact_detector.py` always reports `event_type="toe_off"` as empty (0/0) for this reason - documented in the tool's own docstring and output, not a bug. Detection accuracy is the correct thing to solve first regardless - there's no value in precisely timing a contact the detector can't reliably tell from swing phase.

### 19.5 What was explicitly NOT changed

`contact_events.py`, `sprint_analyzer.py`, `gait_event_evaluator.py`, `gait_event_models.py`, and everything else under `app/services/biomechanics/` and `app/services/quality/` are untouched - confirmed by the full backend test suite staying green (see §19.6). No attempt was made to fix or recalibrate ground-contact detection. No consent-management *system* was built - only a `consent` metadata block in `manifest.json` and a hard process rule in the README (no clip enters the manifest without recorded consent; AI-training consent is tracked as a separate, distinct opt-in) - given this platform's own already-documented concern about apparent-minors' data (§17.6/§17.7), a real dataset of athlete footage is exactly the kind of thing that concern applies to.

### 19.6 Verification

- `cd backend && ./.venv/Scripts/python.exe -m pytest` - **314 passed** (302 prior + 12 new), confirming nothing under `app/` regressed. `tests/test_dataset_tooling.py` covers the screening verdict rules and both `ContactEvent -> GaitEvent`/labels-JSON `-> GaitEvent` conversions as pure logic, imported from `backend/scripts/` the same way those scripts import `app` (sys.path insertion - `scripts/` has no `__init__.py`, same pattern as every other script in that directory).
- **Live**: `screen_clip.py` run against all 3 existing example clips (RTMPose worker running) - all three verdicts came back `marginal`, consistent with §12 (none pass `biomechanics_ready`; none have low enough detection/visibility to `reject` - `my_sprint_3.mp4` and `my_sprint_2.mp4` at 100%/94.4% tracking respectively).
- **Benchmark smoke test caught a real bug before it shipped**: hand-migrated `my_sprint_2.mp4`'s 6 reviewed windows from `tests/fixtures/ground_truth_contact_labels.json` into the new `labels/` schema and ran `benchmark_contact_detector.py`. The first run reported precision 0.0217 (1 true positive, 45 false positives) - technically not wrong, but *misleading*: the tool was counting every one of the ~46 detector firings per side as a false positive the instant it didn't match the single labeled true contact, even though only 6 of those firings had actually been reviewed at all (40 were simply never looked at, neither confirmed right nor wrong). Fixed by restricting predicted events to only those a human actually reviewed (`reviewed_predicted_frame_indices()`, tracked transparently in each report's new `review_coverage` field). Re-run after the fix: **precision 0.1667 (1 true positive, 5 false positives)** - exactly 1/6, matching the already-known "5 of 6 false positives" finding precisely. This is the harness now measuring what it claims to; documented in the README so nobody reports a benchmark number without checking `review_coverage` first.

### 19.7 Exact next task (historical - Athlete Console completion was picked up next as its own architectural priority; see §20)

This phase is done and verified, including the smoke test that caught and fixed the `review_coverage` bug (§19.6) before it could produce a misleading number on real data. `datasets/sprint_biomechanics/labels/my_sprint_2.json` and `benchmarks/my_sprint_2.json` exist from that smoke test (6 hand-migrated windows, not a full review - left as-is, useful as a worked example of the schema) but `my_sprint_2.mp4` was **not** added to `manifest.json`, since it's a pre-existing example clip without a recorded consent entry, not new collected footage - don't treat its presence in `labels/`/`benchmarks/` as a template for skipping the manifest/consent step on real new clips.

The actual dataset-collection work is now unblocked and belongs to the project owner (real footage across varied conditions, per the README's checklist). No further engineering task is implied here until a meaningfully-sized labeled dataset exists to benchmark against - at that point, `benchmarks/_aggregate.json`'s pooled precision/recall/F1 becomes the number a real fix (richer feature set, per §10.1's recommendation, or a different technical approach) needs to beat.

---

## 20. Session update: Athlete Console completion

Same overall session, a distinct piece of work driven by an explicit architectural decision from the project owner: the Athlete Console is the platform's data-producing foundation ("Digital Athlete Passport") - every future consumer (Coach/Academy Console, Talent Discovery, Performance Index) reads from the same canonical athlete record this console produces, so it had to be completed before any further Coach/Academy Console work. **This section is the authoritative current state for the athlete-facing product** - earlier references to `AthleteHome.tsx` as a "thin MVP" and 5 `ComingSoon` athlete routes are now historical.

### 20.1 Audit performed before any code was written

Two read-only audit passes (frontend + DB/security) confirmed, directly from code, not assumption:
- The upload wizard, `useCreatePerformance`/`useAnalysisPolling`/`useRetryAnalysis`, `analysis.service.ts`, `PerformanceHistory.tsx`, `PerformanceProcessing.tsx`, and `AthleteCoaches.tsx` were already solid and reused as-is.
- `AthleteHome.tsx` derived everything from one performances query with two hardcoded static placeholder cards ("Progress Tracking - Coming Next", a bare completion ratio).
- **6 of `athlete_profiles`'s then-10 columns had no writer anywhere in the app** (`height_cm`, `weight_kg`, `secondary_event`, `bio`, `dominant_leg`, `personal_best`) - onboarding only ever set 4 columns, once, at signup.
- No goals, achievements, notifications, or timeline persistence existed anywhere - confirmed by full-repo search, matching §18.3's explicit deferral list.
- **Security**: no cross-user RLS hole found beyond the coach-connection model already built (§18). `analysis_result` is only ever written via the legitimate `useAnalysisPolling` flow. One real (low-severity) fix was identified and made: the coach console's `getAthletePerformances`/`getPerformanceById` reuse (from `PartnerAthleteDetail.tsx`) was selecting the raw `video_url` storage path even though never rendered there - not exploitable (storage RLS already blocks a coach from signing that path) but unnecessary exposure. Two new coach-scoped query functions, `getConnectedAthletePerformances`/`getConnectedPerformanceById` (`features/partners/services/connections.service.ts`), omit `video_url` entirely; the athlete's own `performance.service.ts` queries are untouched and still select it (needed for playback/retry). Two pre-existing, out-of-scope gaps were confirmed still accurate and explicitly not fixed here: `job_id` has no ownership check on the FastAPI side (needs real backend auth infrastructure, its own separate task - §11/§17.7), and a technically savvy athlete could self-edit their own `analysis_result` via devtools (RLS restricts row ownership, not column values - self-harm only, disproportionate to fix with a trigger for this risk level).

### 20.2 Database changes (one migration, purely additive)

`supabase/migrations/0007_add_athlete_goals_and_profile_fields.sql`:
- New `athlete_goals` table (`description`, `target_date`, `status` - active/completed/abandoned), owner-only RLS (`auth.uid() = athlete_id`), same pattern as every other athlete-owned table.
- Three new `athlete_profiles` columns: `ai_training_consent boolean default false` (a real, functional Settings toggle, tracked separately from any other consent - matching the same never-bundle principle established for the coach-console/dataset work in §18/§19), `achievements text` (freeform, same pattern as the existing `bio` column), `deletion_requested_at timestamptz` (backs a "request account deletion" flow that records intent for manual review - does not itself delete anything; no backend cascade-delete endpoint exists).

No changes to any existing RLS policy - the owner-only policies on `profiles`/`athlete_profiles` already permitted everything the new Profile edit page and Goals module needed.

### 20.3 What shipped, mapped to the original step list

- **Dashboard** (`AthleteHome.tsx`, extended) - kept the existing, working performance-derived stat tiles; replaced the two hardcoded placeholder cards with a personal-best card, a recording-quality summary (from the latest analyzed performance), an active-goal card, and a derived notification feed. Added a sport/event/academy badge to the header.
- **Performance History** (`PerformanceHistory.tsx`, extended) - added a recording-quality badge and "Report Ready" indicator per card (derived from `analysis_result`, already fetched, no new query), client-side search (title/notes), event filter, status filter, and sort (newest/oldest/status). No pagination yet - noted as a trigger for later, not built blind.
- **AI Report** (`AnalysisReport` in `PerformanceDetail.tsx`, display-only reorganization, zero logic changes) - now has explicit **AI Analysis** / **Recording Quality** / **Biomechanics** / **Limitations** / **Recommendations** sections instead of warnings+recommendations being one merged list and limitations being buried per-segment. Per-segment inline limitations were removed in favor of one deduplicated top-level Limitations section - the existing `AnalysisReport.test.tsx` was updated to match (a "per-segment limitations" assertion became a "rolled-up limitations" assertion; both still verify the same underlying data renders, just consolidated per the new section structure) rather than the redundant per-segment rendering being kept alongside the new rollup. Added a clearly-marked "Coming Soon" card for Sprint Score / elite-athlete comparison instead of silence.
- **Profile** (`AthleteProfile.tsx` + `athleteProfile.service.ts`, both new) - full edit form for every real `profiles`/`athlete_profiles` column (personal info, sporting info, dominant side, both events, academy, height/weight, bio, achievements, personal best). Reserved, visibly-labeled "Coming Soon" cards for Guardian / Organization-Federation / Discoverability - not hidden, not implemented. Profile photo upload deliberately deferred (see §20.4) - the existing initials-avatar fallback (same pattern as `UserMenu`) is shown instead of a non-functional upload button.
- **Progress** (`AthleteProgress.tsx`, new) - a chronological timeline built entirely from real `performances` rows (upload + analysis-completion events) plus the personal-best value from Profile. No fabricated trend lines or scores - a `TimelineEntry.score` field exists in the type but is never populated, reserved for a future Performance Index to slot into without a rework.
- **Goals** (`AthleteGoals.tsx` + `goals.service.ts`, both new) - CRUD against `athlete_goals`: add a goal (description + optional target date), mark active goals completed or abandoned, delete. No AI-recommendation logic, as instructed.
- **Notifications** - deliberately **derived, not stored** (`features/athlete/lib/deriveNotifications.ts`, pure function, unit-tested + `useAthleteNotifications` hook). All 3 currently-possible notification types (analysis completed, recording quality insufficient, coach connection request) are computed live from data that already exists (`performances`, `coach_athlete_connections`) - no new table, no read/unread sync system. `guardian_approval_required` is a real, typed enum value that is never emitted (no guardian system exists) - satisfies "don't hard-code assumptions that block future modules" without fabricating data. Surfaced on the Dashboard; the hook itself is the reusable "framework" piece, not a dedicated inbox page.
- **Settings** (`AthleteSettings.tsx`, new) - Profile (links to the Profile page), Password (new `changePassword()` in `auth.service.ts` using `supabase.auth.updateUser({password})` - already-available SDK, zero backend change), Privacy and Guardian (reserved cards, explicitly not implemented), AI model training consent (real, functional toggle against the new column), Connected Organizations (reuses `useAthleteConnections` from the coach-console work - real data, not a placeholder), Delete Account (a genuine request-flow with an explicit confirm step - writes `deletion_requested_at`, does not delete anything; withdrawable).
- **Future integration** - satisfied by construction: every new piece is additive and designed around the coach-connection model from §18, so Coach/Academy/Discovery consoles can read the same rows later without a redesign.

### 20.4 Scope decisions made explicitly, not silently

- **Notifications derived, not stored** - see §20.3. Avoids a notifications table + read/unread sync for a v1 that doesn't need it.
- **Profile photo upload deferred** - `profiles.avatar_url` already exists as a column but there's no upload mechanism (bucket, RLS, UI) anywhere in the app. Building that is a second Storage bucket + policies + UI - real new infrastructure, not built this pass. Not a fake upload button either - an honest "coming soon" note next to the existing initials fallback.
- **Delete Account is a request-flow, not real deletion** - no backend cascade-delete endpoint exists, and account deletion is exactly the kind of high-blast-radius action that shouldn't be wired as a casual self-service DB cascade. A human reviews the request.
- **Achievements got a real column** (`achievements text`) since it was explicitly asked for and cheap to add - no new structured/list UI, freeform text like `bio`.

### 20.5 Verification

- `cd backend && ./.venv/Scripts/python.exe -m pytest` - **314 passed**, confirmed untouched (nothing under `backend/` changed this pass).
- `cd frontend && npm run test` - **39 passed** (30 prior + 8 new `deriveNotifications` cases + 1 new `AnalysisReport` regression test for the section-header restructuring). `npx tsc -b --force` - clean throughout every step of this build, not just at the end.
- **Live, verified**: Dashboard (profile summary badge, notification feed correctly showing "Analysis complete" and "Recording quality issue" for the real seeded performance, empty states for personal-best/goals since migration `0007` wasn't applied yet at verification time - confirmed the app degrades gracefully rather than crashing when new columns/tables don't exist yet), Performance History (recording-quality badge, Report Ready badge, search with a real no-matches empty state), the restructured `AnalysisReport` (AI Analysis / Recording Quality / Biomechanics / Limitations / Coming Soon all rendering as distinct sections on a real completed performance), and the coach console post-security-fix (`PartnerAthleteDetail.tsx` still renders the connected athlete's profile and performance history correctly with `video_url` removed from its query). Zero console errors and zero dev-server errors throughout.
**Follow-up pass, after the project owner ran migration `0007`**: all four DB-dependent pieces were live-verified against real rows, signed in as the same seeded QA athlete account used throughout this project:
- **Profile edit round-trip**: set Personal Best to "11.42s (100m)" and Dominant Side to "Right", saved ("Profile saved." confirmation shown), reloaded the page - both values persisted correctly.
- **Goals CRUD**: added a goal ("Break 11.5s in the 100m", target date 1 Dec 2026) - appeared instantly under "Active"; clicked Mark Complete - moved to "Past" with a "Completed" badge; deleted it - back to the "No goals yet" empty state. Full lifecycle confirmed.
- **AI training consent toggle**: checked it, reloaded, still checked - confirmed persisted, not just optimistic UI.
- **Delete-account request/withdraw cycle**: clicked "Request Account Deletion" - Cancel correctly backed out with no write; confirmed "Yes, request deletion" - state changed to "Deletion requested. Our team will follow up." with a reload confirming persistence; clicked "Withdraw request" - correctly reverted to the initial button state.
- **Cross-page consistency confirmed as a side effect**: the Dashboard's Personal Best card, the Progress page's Personal Best card, and the Profile page all independently read the same freshly-saved value correctly - and the Dashboard's greeting switched from the email-derived fallback to the real saved full name ("QA Test Athlete") once the profile query had real data to read. Settings' "Connected Organizations" card correctly showed the real existing coach connection (`QA Test Coach`) via the reused `useAthleteConnections` hook - confirming that reuse works in a third consumer, not just the two it was built for.
- Zero console errors and zero dev-server errors across the entire verification pass, on both the athlete and coach sides.

### 20.6 Exact next task (historical - profile photo upload was picked up next; see §21)

This phase is done and fully verified, including every DB-dependent piece. Coach/Academy Console work may resume per the project owner's own gating instruction, now that the Athlete Console is feature-complete against the original 10-step spec. Two smaller items worth a pass whenever convenient, not urgent: profile photo upload (§20.4, needs a new Storage bucket) and a dedicated Reports page distinct from Performance History + Progress (currently `reports` stays `ComingSoon` with a note pointing at the two real pages that already cover it - revisit only if that turns out to be insufficient in practice).

---

## 21. Session update: profile photo upload

Closes the last item deferred from Athlete Console completion (§20.4). Coach/Academy Console resumes after this, per the project owner's own sequencing.

### 21.1 Design decision: private bucket, signed URLs - not public

The coach-connection model (§18) gates *all* athlete data behind an accepted connection - a coach can't see an athlete's name, event, or performances without one. A public `avatars` bucket would have broken that model outright: anyone with the URL could view an athlete's photo with zero relationship to them, a real problem given this platform's repeated, explicit concern about apparent-minors' data. So: new `avatars` bucket, **private**, same folder-scoped `{userId}/...` ownership pattern already proven for `performance-recordings`. `profiles.avatar_url` stores the **storage path**, not a URL (same convention as `performances.video_url`); a signed URL is minted client-side on demand, reusing the exact pattern `createSignedVideoUrl()` already established in `analysis.service.ts`, just with a longer expiry (1 hour vs. 10 minutes) since avatars are shown on every page load rather than downloaded once.

Storage key is fixed per user (`{userId}/avatar`, no extension in the key - `contentType` is set explicitly on upload) with `upsert: true`, so re-uploading always replaces the same object instead of accumulating orphaned files.

### 21.2 Database changes

`supabase/migrations/0008_add_avatars_bucket.sql` - `insert into storage.buckets` for `avatars` (private, 5MB limit, `image/jpeg`/`image/png`/`image/webp` only) plus 4 folder-scoped RLS policies on `storage.objects` (select/insert/update/delete, all `(storage.foldername(name))[1] = auth.uid()::text`). Bucket created via SQL rather than the dashboard - more reproducible than how `performance-recordings` was originally set up (an undocumented manual step, per the audit in §20.1).

### 21.3 What shipped

- `features/athlete/services/avatar.service.ts` (new) - `validateAvatarFile` (pure, unit-tested: type/size checks), `uploadAvatar`, `removeAvatar`, `getAvatarSignedUrl`.
- `features/athlete/hooks/useAvatarUpload.ts` (new) - `useAvatarSignedUrl` (shared by any component that needs to render a photo from its storage path), `useUploadAvatar`, `useRemoveAvatar`.
- `AthleteProfile.tsx` - the static "Photo upload is coming soon" note replaced with a real `AvatarUploader`: click the avatar circle or a text link to pick a file, instant local preview via `URL.createObjectURL` while the upload is in flight, inline validation errors, a "Remove" option once a photo exists.
- `UserMenu.tsx` - shows the real photo (signed URL) instead of initials once one exists. Deliberately does **not** reuse `useAthleteProfile` (which also queries `athlete_profiles`, a table coach/academy accounts have no row in) - a small standalone `useOwnAvatarPath` query selects only `profiles.avatar_url`, the one column every role actually has, keeping this shared-across-all-three-layouts component role-agnostic.

### 21.4 A real bug caught during live verification, fixed before shipping

First live pass: removing a photo correctly updated the Profile page (via `useAthleteProfile`'s invalidation) but the header `UserMenu` kept showing the stale photo until a full page reload - `useUploadAvatar`/`useRemoveAvatar` only invalidated the `["athlete-profile", userId]` query key, not `UserMenu`'s separate `["own-avatar-path", userId]` cache (intentionally separate, per §21.3's reasoning, but that meant it needed its own invalidation, which was missed on the first pass). Fixed by having both mutations invalidate both query keys (plus the `["avatar-signed-url", path]` cache itself, so a same-path upsert re-upload doesn't keep serving a stale cached signed URL). Re-verified live: removing a photo now updates the Profile page and the header instantly, no reload needed.

### 21.5 Verification

- `validateAvatarFile` unit tests (5 cases: valid JPEG/PNG/WebP, rejects non-image, rejects oversized, accepts exactly-at-limit) - all passing. Full frontend suite: **44 passed** (39 prior + 5 new). `cd backend && pytest` unaffected (nothing under `backend/` changed) - **314 passed**. `npx tsc -b --force` clean throughout.
- **Live, both migration-dependent and cross-account checks done**: the Browser pane's automation can't drive a native file picker (same limitation noted for video upload in §17.1's audit trace), so the upload path was exercised via the same real REST/API sequence the app's own `uploadAvatar()` makes (authenticate as the real seeded QA athlete, `POST` an image to `/storage/v1/object/avatars/{userId}/avatar`, `PATCH profiles.avatar_url`) - not a shortcut, the exact same calls the UI performs. Confirmed the athlete could self-sign the resulting path (200). **Confirmed the private bucket actually blocks cross-account access**: authenticated as the separate seeded QA coach account and attempted to sign the athlete's avatar path directly - rejected (`404 Object not found`, Supabase Storage's standard RLS-denial response, deliberately not `403` to avoid leaking existence information). Reloaded the Profile page in the real browser afterward and confirmed the photo rendered correctly in both the Profile page and the header `UserMenu` via the app's own signed-URL flow - not just the raw REST calls. The remove flow (§21.4) was exercised entirely through real UI clicks, no REST shortcut needed for that half. Zero console or server errors throughout.

### 21.6 Explicitly out of scope (unchanged from the plan, not silently expanded)

No image cropping/editing - raw upload only. No avatar visibility for coach/academy views yet - not requested; a `coach_athlete_connections`-gated `storage.objects` SELECT policy on this bucket would be the natural extension, same shape as the existing performance-data policies, when actually needed. No avatar in Talent Discovery (doesn't exist yet).

### 21.7 Exact next task (historical - an Athlete Console UI/feature pass was picked up next instead; see §22)

This phase is done and verified. Per the project owner's own sequencing, **Coach/Academy Console work resumes next** - the Athlete Console (§20) is feature-complete, and this was the last item explicitly deferred from it. See §17.4/§18 for what already exists there (real onboarding, a `PendingConsole`-replaced roster/notes/requests flow for the connected-athlete relationship) versus what a fuller Coach/Academy Console still needs (talent search/discovery, report comparisons, shortlists - none of which exist yet, all deliberately deferred pending real usage data per §18.6's original framing). Terms/Privacy remains explicitly parked per the project owner's own instruction until every other important platform aspect is done - do not pick it up unprompted despite the apparent-minors-data urgency flagged in §17.6/§17.7.

**What actually happened**: before starting Coach/Academy Console work, the project owner asked for one more Athlete Console pass - UI polish and feature gaps identified by a live audit rather than a pre-set list. See §22. Coach/Academy Console (talent search/discovery, report comparisons, shortlists) is still the next task after that.

---

## 22. Session update: Athlete Console UI/feature pass

Same overall codebase, a fresh session. The project owner asked to develop the Athlete Console further "in terms of UI and features," with priority left to this session's own judgment ("both, my call on priority") rather than a pre-set list. **Code is not yet committed to git as of this writing** - that's the project owner's call, per this repo's standing convention.

### 22.1 Audit performed before any code was written

Signed in as the seeded QA athlete (`shakti.qa.athlete@example.com`) in a real browser and walked every athlete-facing page (Dashboard, Performance History, Performance Detail/Report, Progress, Goals, Coaches, Profile, Settings), then checked the mobile viewport and read the relevant source files directly rather than trusting the doc's own "feature-complete" claim from §20. Found:

- **A real, confirmed bug, not a polish item**: `AthleteLayout.tsx`'s sidebar was `hidden lg:block` with **zero mobile fallback** - no hamburger, no drawer, nothing. Below 1024px width, an athlete could see the Dashboard and nothing else; Performances/Coaches/Progress/Goals/Reports/Profile/Settings were all unreachable. Given this platform's own stated design principle ("design for real Indian filming conditions - phone cameras," §13), this was the highest-priority finding.
- **The AI Report (the actual product) was 100% plain tables** - biomechanics readiness checks and visibility percentages were text-in-a-table-cell with a pass/fail badge, no gauges or bars anywhere.
- **Progress page was a bare vertical timeline** with two stat tiles - no trend visualization despite being the natural home for one.
- **Reports** (`/console/athlete/reports`) was still a literal `ComingSoon` stub. With real multi-session data now flowing through the seeded QA account, the doc's own §20.6 "revisit only if insufficient" condition was judged met.
- **Discover**, **Score Progression**, and the Guardian/Organization-Federation reserved cards were confirmed still correctly deferred (blocked on other unbuilt systems - Coach Console discovery, a future Performance Index, and a guardian model respectively) - explicitly left untouched.

Proposed priority order was confirmed with the project owner before any code: (1) mobile nav fix, (2) AI Report/Progress data visualization, (3) real Reports page, (4) smaller polish (goal reminders, empty-state variety).

### 22.2 Mobile navigation fix

`AthleteLayout.tsx` - extracted the nav-item rendering into a small internal `AthleteNavLinks` component (shared between the desktop sidebar and the new mobile drawer, avoiding a second copy of the same 9-item list) and added a hamburger button (`lg:hidden`) in the header that opens a fixed, backdrop-blurred slide-in drawer with the same nav, sign-out button, and a close button. Tapping any link closes the drawer via an `onNavigate` callback. Live-verified at the mobile viewport (375×812): the drawer opens, all 9 links are reachable, and tapping "Reports" both navigated and closed the drawer correctly.

**Not touched, but confirmed to have the identical bug**: `PartnerLayout.tsx` (coach/academy console) uses the exact same `hidden lg:block` sidebar pattern with no mobile fallback. Out of scope for this athlete-focused pass - worth fixing whenever Coach/Academy Console work resumes (§21.7).

### 22.3 AI Report and Progress data visualization

All additive - no changes to what data is computed, gated, or fetched; every existing `AnalysisReport.test.tsx` assertion (44 cases) still passes unmodified, since all new visuals were added alongside existing text rather than replacing it.

- `PerformanceDetail.tsx`: added a `ScoreGauge` (lightweight inline SVG radial - no charting library added) for the overall biomechanics-readiness score at the top of the skipped-biomechanics breakdown; extended `CheckRow`/`buildGatingChecks`/`buildQualityChecks` with an optional `percent` field (only populated for checks that are inherently a 0-100 score - left `undefined` for the categorical "Camera angle" check rather than fabricating a number); added a "Level" bar column to `CheckTable` that reads that field; extended `StatTile` with an optional `percent` prop (renders a thin bar under the value) and used it for Detection Rate, Duty Factor, and Knee Symmetry; replaced the plain-text Recording Quality rating with a color-coded `RatingBadge` (Excellent=green, Good=blue, Fair=amber, Poor=red). `RatingBadge` was exported (previously module-private) for reuse in the new Reports page (§22.4).
- `AthleteProgress.tsx`: added a `ReadinessTrendChart` - a small SVG-free bar chart (plain divs with computed heights) plotting each completed session's `analysis_readiness.score` in chronological order. **Deliberately not the same thing as the existing "Score progression" reserved card** (§20.4's future Performance Index, still correctly un-built) - labeled explicitly as a recording-quality trend, not an athletic score, so the two aren't confused. Handles 0 and 1 data points gracefully (the seeded QA account only has one performance; live-verified it renders a single labeled bar rather than breaking).

### 22.4 Real Reports page

`AthleteReports.tsx` (new) replaces the `ComingSoon` stub at `/console/athlete/reports` (route added to `AppRouter.tsx`, new `ROUTES.ATHLETE.REPORTS` constant). Shows only performances with a completed analysis (`upload_status === "completed" && analysis_result`) - a deliberately narrower set than Performance History, which shows every upload regardless of status. Each row shows the `RatingBadge`, a biomechanics-included/skipped badge, readiness score, detection rate, and camera view, linking to the full report. Filterable by event and sortable (newest/oldest/highest readiness score), with three distinct empty states: no performances at all, performances exist but none completed yet (distinct from "no matches" - points at Performance History for status), and no matches for the current filter. Live-verified: renders the seeded QA performance correctly, filter/sort controls work, and clicking through navigates to the correct full detail page.

### 22.5 Goal target-date reminders and empty-state polish

- `deriveNotifications.ts`: added a new `goal_target_date` notification type and a pure `deriveGoalNotifications()` helper (takes an explicit `now: Date` parameter rather than calling `new Date()` internally, keeping the function deterministically testable like the rest of the file). Active goals with a target date within 7 days emit an "approaching" reminder; active goals past their target date emit an "overdue" reminder; completed/abandoned goals and goals with no target date emit nothing. Wired through `useAthleteNotifications.ts` (now also fetches goals via the existing `useAthleteGoals` hook - no new query shape) and given an icon case (`Target`) in `AthleteHome.tsx`'s notification renderer. 5 new unit tests added (49 total, up from 44); live-verified by adding a real goal 2 days out through the actual UI and confirming "Goal target date approaching" appeared correctly in the Dashboard's notification feed, then cleaned up.
- New `components/shared/EmptyState.tsx` - a small shared component (icon in a colored circular badge, title, description, optional action) replacing the identical hand-duplicated `border-dashed` block that existed in 7 files. Applied to the 5 athlete-facing occurrences (`AthleteGoals`, `AthleteProgress`, `PerformanceHistory`, `AthleteReports`, `AthleteCoaches`). A `tone` prop distinguishes genuine first-run empty states (`"primary"` - warm orange icon badge, used for "no goals/performances/reports/coaches yet") from search/filter-yielded-nothing states (`"neutral"` - muted gray, used for "no matches") - the two are conceptually different (one is a call to action, the other isn't) and are now visually distinguished instead of looking identical.
- **Not touched**: `PartnerRoster.tsx`/`PartnerHome.tsx` (coach/academy console) use the same old duplicated pattern - out of scope for this athlete-focused pass, worth converting to `EmptyState` whenever Coach/Academy Console work resumes.

### 22.6 Verification

- `cd frontend && npm run test` - **49 passed** (44 prior + 5 new goal-reminder cases). `npx tsc -b --force` - clean, checked after every task in this pass, not just at the end.
- `cd backend && pytest` not re-run - nothing under `backend/` changed this session.
- **Live, in a real browser, signed in as the seeded QA athlete account**: every page in this section was re-verified after its corresponding change (not just once at the end) - mobile drawer open/close/navigate at 375×812, the readiness gauge and Level bars rendering with correct colors on the real seeded performance (49/100 readiness, correctly red; 100% detection, correctly green), the Progress page's single-bar trend chart, the new Reports page's filter/sort/empty-states and click-through to the full report, the goal reminder appearing in the Dashboard notification feed after a real goal was added through the UI (then removed to leave the QA account clean), and the `EmptyState` circular icon badge rendering correctly on Goals. Zero console errors and zero dev-server errors throughout.

### 22.7 Exact next task (current, supersedes §21.7)

This phase is done and verified. Per the project owner's own sequencing, **Coach/Academy Console work resumes next** - talent search/discovery, report comparisons, and shortlists, none of which exist yet (confirmed via a separate audit earlier in this session: `PartnerRoster.tsx` is a flat unselectable list, and the connection-gated RLS model means a coach/academy currently has zero visibility into any athlete outside an existing connection - the athlete Profile page's own reserved "Discoverability" placeholder confirms an opt-in flag was the intended shape, not open browsing). Two small carry-forward items when that work is picked up: `PartnerLayout.tsx` has the identical mobile-nav bug fixed in §22.2 for the athlete side, and `PartnerRoster.tsx`/`PartnerHome.tsx` could reuse the new `EmptyState` component from §22.5. Terms/Privacy remains explicitly parked per the project owner's own instruction - do not pick it up unprompted.
