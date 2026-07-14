# Shakti Sports AI — Engineering Handoff

**Read this document fully before touching code.** It assumes zero memory of prior work. Where something is uncertain, unverified, or was deliberately left broken, that is stated explicitly — do not assume silence means "done and correct."

Last updated: 2026-07-14, after commit `b6b75cf` on `main`.

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
docs/             This file, and nothing else yet
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
    router/AppRouter.tsx           React Router config - INCOMPLETE, see §11
    layouts/                       MarketingLayout, AuthLayout
    pages/HomePage.tsx
  features/
    auth/                          Sign in/up, role selection, onboarding (athlete only is routed - see §11)
    athlete/                       Dashboard (AthleteLayout has 5 of 7 nav links with no matching route)
    performances/                  Upload wizard, performance history/detail/report pages
    home/                          Marketing page sections
  components/ui, layout, shared    Design system components
  constants/routes.ts, navigation.ts, roleNavigation.ts
  lib/supabase.ts                  Supabase client init
  theme/                           Design tokens
```

**Critical fact: the frontend does not call the FastAPI backend at all.** `features/performances/services/performance.service.ts` talks directly to Supabase (storage upload + table inserts). There is no fetch/axios call anywhere in the frontend to `/api/analyze/video` or any other backend route. The two halves of this product are not wired together yet.

---

## 3. High-level architecture

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

Everything else is **inferred from frontend Supabase query code** (`frontend/src/features/*/services/*.ts`), not from any migration file:

- **`profiles`** — `id` (uuid, = auth user id), `email`, `role` (`athlete`/`coach`/`academy`/`admin`), `full_name`, `state`, `district`.
- **`athlete_profiles`** — `id` (uuid, fk to profiles), `date_of_birth`, `gender`, `preferred_event`, `academy`.
- **`events`** — `id`, `name` (e.g. `"Sprint"`, `"Hurdles"`, `"Long Jump"`, `"High Jump"`), `category`. Looked up by name from `EVENT_NAME_MAP` in `performance.service.ts` (`"100m"→"Sprint"`, `"110h"→"Hurdles"`, `"long_jump"→"Long Jump"`, `"high_jump"→"High Jump"`).
- **`performances`** — `id`, `athlete_id` (fk), `event_id` (fk), `performance_number` (sequential per athlete), `title`, `performance_date`, `attempt_number`, `video_url`, `upload_status`, `notes`, `created_at`.
- **Storage bucket**: `performance-recordings` — video files stored at `{athleteId}/{uuid}.{ext}`.

**Action item for whoever picks this up:** find and check in the actual Supabase migration/schema (via `supabase db dump` or the dashboard's SQL editor export), or write one from the inferred schema above and verify it against the live project. Right now there is no way to recreate the database from this repo alone.

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

---

## 11. Known limitations (current, as of `b6b75cf`)

- **Ground-contact timing is not trustworthy for bad camera angles.** See §10. `contact_time_ms`, `flight_time`, `duty_factor` should not be shown to end users as authoritative numbers until this is properly solved.
- **Camera angle, not the algorithm, looks like the dominant variable** for ground-contact accuracy — confirmed the same unmodified detector went from 0/9 visually-correct samples on a bad-angle clip to 3/6 on a good-angle clip — but this is not independently quantified with frame-level error for good-angle footage. Treat as a strong signal, not a closed case.
- **Left vs. right leg-split asymmetry is unexplained.** In `stride_velocity_bridge.py` work, left-side same-frame leg-split values trended suspiciously near zero compared to a clean, sustained right-side signal. Could be a real gait asymmetry in the specific athlete filmed, or a timing/detection quirk specific to left-side contact events. Not root-caused.
- **`detect_sprint_phases` can't represent a "settled at new pace" scenario** — see bug #6's residual limitation above.
- **Job queue is in-memory and single-process.** State is lost on restart; will not work correctly across multiple server worker processes (requests could round-robin to a process that never ran the job). Needs a Redis/DB-backed store or a real task queue (Celery/RQ) before scaling beyond one process.
- **MediaPipe fallback is not automatic.** If the RTMPose worker is down, `/api/analyze/video` jobs fail with a clear error; nothing currently switches to the MediaPipe path automatically.
- **`app/services/pose_adapters/` is dead code.** `RTMPoseAdapter` + `registry.py` are never imported by any live or CLI code path, and its expected input format (raw MMPose-style `keypoints` list + parallel `keypoint_scores` list) doesn't match what the actual worker returns (a dict keyed by joint name, already normalized). If someone wires this up later expecting it to work like the rest of the pipeline, it will silently misbehave. Flagged, never fixed or removed.
- **Only sprint has been validated.** Hurdles/long jump/high jump code exists but has never touched real footage.
- **`backend/app/services/{digital_twin,digital_twin_v2,physics,fusion,motion,coach,talent,validation,research,readiness,athlete_intelligence,feature_store,pipeline}/`** — substantial code, zero validation this session. Unknown state.
- **`reports/coach.py`, `reports/scoring.py`, `reports/recommendations.py`** are empty 1-line stub files.
- **Database schema is not version-controlled** beyond one table (`digital_twin_v2/supabase_schema.sql`). See §5.
- **Frontend routing is broken in several places** (not backend, but worth knowing): coach/academy onboarding pages exist as components but aren't wired into `AppRouter.tsx`; 5 of 7 athlete-dashboard sidebar links (`reports`, `progress`, `discover`, `profile`, `settings`) have no matching route; no 404/catch-all route exists; marketing nav anchor links (`#platform`, `#sports`, etc.) point to page sections that don't have matching `id` attributes. A background task was flagged for this but not yet actioned.
- **Frontend is not connected to the backend at all.** See §2/§3.
- **`backend/requirements.txt` is UTF-16 encoded** (unusual; works with `pip install -r` but reads oddly with plain text tools — use `iconv -f UTF-16 -t UTF-8` to view it normally).
- **No authentication, rate limiting, or file-size limits** on the `/api/analyze/video` endpoint.

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
- **Steps 7-9 (AI coach feedback, sprint score, elite comparison)** — not started. `reports/coach.py`/`scoring.py`/`recommendations.py` are empty stubs. **Elite comparison specifically flagged as needing real licensed reference data before attempting — a claims/liability risk, not just an engineering task.**
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
b6b75cf  feat: wire RTMPose into the live API                                 (bug #9) <- HEAD, current tip
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
  3. `cd frontend && npm run dev` — start the frontend (Vite, default port 5173). Note: frontend won't actually call the backend (see §2/§11).
  4. To run tests: `cd backend && ./.venv/Scripts/python.exe -m pytest` (no args needed — `pytest.ini` scopes collection correctly).
- **Environment variables**:
  - `backend/.env.rtmpose-live.example` documents the worker's own config: `RTMPOSE_MODEL`, `RTMPOSE_DEVICE` (default `cuda:0`), `RTMPOSE_SCHEMA` (`halpe26`), `RTMPOSE_MIN_CONFIDENCE` (`0.35`), `RTMPOSE_MAX_PEOPLE` (`4`), optional `RTMPOSE_DET_MODEL`.
  - `RTMPOSE_WORKER_URL` (new this session, in `live_analyzer.py`) — base URL the main backend uses to reach the worker, default `http://127.0.0.1:8011`.
  - `frontend/.env.local` — `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`.
  - No `.env.example` exists for the main backend's own config (CORS origin, temp dir, etc. are currently hardcoded in `main.py`/`routes.py`, not env-driven).

---

## 16. Exact next task

Two candidate next tasks were under discussion when this handoff was written; neither has been started. Pick based on what the requester actually wants:

**Option A — Frontend integration (Step 19).** Wire the frontend's performance-upload flow to actually call `/api/analyze/video` and poll for results, instead of only writing to Supabase. This is the single biggest gap between "backend works" and "product works." Requires: an HTTP client call in `performance.service.ts` (or a new service file) to submit the uploaded video to the backend after/instead of the Supabase storage upload, a polling mechanism (the `PerformanceProcessing.tsx` page already exists as a likely home for this), and a decision about where the analysis result gets stored (write back to Supabase `performances` table? A new table?). Also fix the known broken routes while touching this area (§11).

**Option B — Ground-contact detection, properly this time.** Do not attempt another single-clip heuristic. Get (or synthesize) more labeled ground-truth data — ideally several more real clips at varying camera angles/heights/distances, each hand-labeled for true contact frames the way `tests/fixtures/ground_truth_contact_labels.json` was — and either (a) properly calibrate a heuristic against a real dataset instead of 3-4 clips, or (b) consider a small trained classifier if heuristics keep failing. This directly gates whether `contact_time_ms`/`flight_time`/`duty_factor` can ever be shown to users as trustworthy numbers.

**Recommendation if forced to choose one**: Option A. The backend biomechanics work has reached a point of diminishing returns without more real labeled data (which requires either the requester sourcing footage or waiting for real user uploads); the frontend gap, by contrast, is pure engineering work with everything needed already in the repo, and closing it is what turns this from "a validated backend" into "a working product" that could start generating the real user footage Option B actually needs.

Whichever is chosen: run `cd backend && ./.venv/Scripts/python.exe -m pytest` first to confirm the starting state is clean (294 passing), and re-read §11 in full before writing any code — several of those limitations are easy to accidentally reintroduce or build on top of without realizing it.
