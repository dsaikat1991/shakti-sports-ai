# Sprint biomechanics research dataset

**This is a research/data-collection area. It does not change, gate, or feed into the production biomechanics pipeline in any way.** Nothing under `app/services/` reads from this directory. Its only purpose is to make future work on ground-contact detection (and anything downstream of it) evidence-based instead of another guess.

Read `docs/ENGINEERING_HANDOFF.md` §10/§10.1 first if you haven't — it documents *why* this exists: ground-contact detection is confirmed unreliable for some camera angles, with a direct quantified counterexample (a confirmed true contact scored *lower* on the detector's only signal than a confirmed false positive). That rules out threshold tuning as a fix. Further engineering effort on the heuristic itself is paused. This directory is where the next real attempt gets its evidence from.

## Why one label type covers three research questions

`app/services/biomechanics/flight_time.py`'s `estimate_flight_times()` and `estimate_duty_factor()` both take **ground-contact events** as their only real input — flight time is the inter-contact gap, duty factor is contact-time vs. flight-time. So labeling ground-contact events well is the one thing that unlocks validation for ground-contact detection, flight-time estimation, *and* duty-factor, plus gives any future ML approach real training/eval data, plus gives any future heuristic a real benchmark to beat. There is deliberately no separate "flight-time dataset" or "duty-factor dataset" — it's the same labels, used three ways.

## Honest scope: what this dataset can and can't validate yet

Labels captured by this workflow record **a single representative timestamp per contact** (matching the detector's own `peak_timestamp_ms` semantics, and matching the proven hand-review methodology this is built on). That's enough to measure ground-contact **detection accuracy** — precision, recall, and timing error on *whether* and *roughly when* a contact happened.

It is **not** enough to tightly validate flight-time or duty-factor, which need the contact's *start and end* (a full stance interval) labeled, not just one point. Labeling a stance interval reliably from video is a harder, slower task than judging "is this a contact" — and there's no point solving that harder problem before the detector can reliably tell contact from swing in the first place. So: **Phase 1 (this) is single-point contact labels, aimed at fixing detection accuracy first.** The label schema below has a documented (currently unused) slot for stance-interval labels so Phase 2 doesn't require a schema rewrite.

## Directory layout

```
backend/datasets/sprint_biomechanics/
  README.md              this file
  manifest.json           master index of every clip - checked into git, no video
  clips/                  raw video - gitignored, never committed
  screening/<id>.json      one per clip - automated pre-labeling triage report
  labels/<id>.json         one per clip - structured human labels
  benchmarks/<id>.json     one per clip - detector-vs-labels evaluation report
  benchmarks/_aggregate.json   dataset-wide rollup across every benchmarked clip
```

## Workflow: screen → label → benchmark

### 0. Capture

Record real footage. Every clip needs, at minimum, **consent** to use it for this purpose (see below) — get that before you record, not after. Prioritize *variety* over volume — the goal is a dataset that spans the conditions real users will actually upload from, not another three clips of the same setup:

- **Camera angle**: true side-on (the required view) *and* deliberately bad angles (three-quarter, low/close/oblique) — the bad ones are exactly what exposed the current bug, and are valuable, not throwaway.
- **Camera height**: waist-height (correct) and clearly wrong (too low/tilted up) — both are useful data points.
- **Distance**: close and far framing.
- **Lighting**: daylight, overcast, indoor, evening/low-light.
- **Location/background**: different ground textures and backgrounds (a uniform brick-paver background already blocked confident labeling once — busy/textured grounds are a real variable, not noise to avoid).
- **Device**: phones vary a lot in stabilization/rolling-shutter; mix devices if you can.
- **Athletes/events**: different body types, running styles, and (once hurdles/long jump/high jump matter) event types.

Drop the raw file into `clips/` (or anywhere convenient — the manifest just needs a path). It will not be committed to git.

### 1. Screen

```
cd backend
./.venv/Scripts/python.exe scripts/screen_clip.py clips/my_new_clip.mp4
```

Requires the RTMPose worker running (`uvicorn rtmpose_worker.app:app --port 8011`, same as every other analysis tool in this repo). This runs the exact same tracking + quality-gate pipeline the production API uses (`live_analyzer.analyze_video()` — zero reimplemented logic) and writes `screening/<clip_id>.json` with a verdict:

- **`reject`** — tracking too unreliable, or the foot isn't visible enough to judge contact vs. swing even in principle. Not worth labeling.
- **`marginal`** — labelable, but fails the production `biomechanics_ready` gate (bad angle/height/etc). **Still label these** — this is exactly the failure mode under investigation.
- **`accept`** — passes the full quality gate. Still worth a quick human look before investing in full labeling — the automated gate is necessary but not sufficient (a clip once scored a perfect camera-height score and was *still* unusable, due to background occlusion the gate has no way to see).

### 2. Get a tracked timeline

```
./.venv/Scripts/python.exe scripts/analyze_clip.py clips/my_new_clip.mp4 --json timeline/my_new_clip.json
```
(Existing tool, unchanged. Also requires the worker running.)

### 3. Label

```
./.venv/Scripts/python.exe scripts/label_contact_frames.py \
  --timeline timeline/my_new_clip.json --video clips/my_new_clip.mp4 \
  --side right --out tiles/ --mode candidates \
  --emit-label-skeleton labels/my_new_clip.json
./.venv/Scripts/python.exe scripts/label_contact_frames.py \
  --timeline timeline/my_new_clip.json --video clips/my_new_clip.mp4 \
  --side right --out tiles/ --mode uniform \
  --emit-label-skeleton labels/my_new_clip.json
# repeat both modes for --side left
```
`candidates` mode audits the detector's own fired peaks (is each one really a contact?); `uniform` mode surfaces contacts the detector missed entirely (false negatives), which `candidates` mode structurally cannot see. Run both, for both sides. Open the generated tile grids, and for each window fill in `verdict`/`confidence`/`labeled_frame_index`/`reasoning` directly in `labels/my_new_clip.json` — the skeleton is pre-filled with everything the detector already knows (window frames, its own peak estimate); you're only recording your own visual judgment.

Re-running `label_contact_frames.py` (e.g. after a detector change moves the candidate windows) merges by `window_frames` rather than overwriting, so previously-reviewed windows aren't lost.

### 4. Benchmark

```
./.venv/Scripts/python.exe scripts/benchmark_contact_detector.py \
  --timeline timeline/my_new_clip.json --labels labels/my_new_clip.json
```
Runs the real, unmodified production detector (`app.services.biomechanics.contact_events`) against the same tracked timeline, compares its output to your labels using `app.services.biomechanics.gait_event_evaluator` (precision/recall/F1/timing-error — already-existing, already-tested code, just never connected to real ground truth before this), and writes `benchmarks/my_new_clip.json`.

**Important**: precision/recall are computed only over detector-fired events a human actually reviewed (tracked in the report's `review_coverage` field, `detector_events_reviewed` vs. `detector_events_total`). An unreviewed detector firing is neither a confirmed hit nor a confirmed miss, so it's excluded rather than counted as an automatic false positive - otherwise a sparse label set (e.g. `uniform` mode sampling 6 windows out of 46 total detector firings) would silently inflate the apparent false-positive rate for every event nobody looked at. This means the numbers only describe how good the detector is *on the specific windows you reviewed* - review more of a clip's detector firings (or use `uniform` mode with a higher `--uniform-count`) for a number that covers more of it.

To roll up every labeled clip in the dataset at once:
```
./.venv/Scripts/python.exe scripts/benchmark_contact_detector.py --manifest datasets/sprint_biomechanics/manifest.json
```
writes `benchmarks/_aggregate.json` — the single number to watch as the dataset grows, and the baseline any future detector (heuristic or ML) needs to beat.

### 5. Register in the manifest

Add an entry to `manifest.json` with the clip's capture metadata, athlete info (pseudonym, not real name), consent block, and status flags. See the schema below.

## Schemas

### `manifest.json` entry
```json
{
  "clip_id": "2026-07-20_pune_track_side_evening_001",
  "video_path": "backend/datasets/sprint_biomechanics/clips/2026-07-20_pune_track_side_evening_001.mp4",
  "added_at": "2026-07-20T18:04:00+05:30",
  "capture": {
    "location_description": "Local athletics track, Pune",
    "date": "2026-07-20",
    "device": "iPhone 13, rear camera",
    "resolution": "1920x1080",
    "fps": 60,
    "camera_setup": { "intended_view": "side", "intended_height": "waist", "distance_m": 8 },
    "lighting": "outdoor_evening",
    "notes": "Slight downhill grade on the track."
  },
  "athlete": { "pseudonym": "athlete_A", "age_bracket": "adult", "event": "100m" },
  "consent": {
    "recorded_by": "project_owner",
    "consent_obtained": true,
    "consent_type": "adult_self",
    "model_training_opt_in": false,
    "date": "2026-07-20"
  },
  "status": {
    "screened": true, "screening_verdict": "accept",
    "labeled": true, "label_sets": ["ground_contact_peak"],
    "benchmarked": true
  }
}
```

### `labels/<clip_id>.json`
```json
{
  "schema_version": "1.0",
  "clip_id": "...",
  "source_timeline": "path to the analyze_clip.py --json timeline used",
  "label_sets": {
    "ground_contact_peak": {
      "methodology": "candidates+uniform tile review via scripts/label_contact_frames.py",
      "reviewer": "...", "reviewed_at": "...",
      "sides": {
        "left": [
          {
            "window_source": "candidates|uniform", "window_frames": [120, 134],
            "detector_peak_frame_index": 127, "detector_peak_timestamp_ms": 2116,
            "verdict": "true_contact|false_positive|inconclusive|unusable",
            "confidence": "low|medium|high",
            "labeled_frame_index": 128, "labeled_timestamp_ms": 2133,
            "reasoning": "Heel and toe both visibly touching ground, weight-bearing posture."
          }
        ],
        "right": []
      }
    }
  }
}
```
`labeled_frame_index`/`labeled_timestamp_ms` stay `null` unless `verdict` is `true_contact`. `label_sets` is a dict, not a flat list, specifically so a future `stance_interval` label set (Phase 2, start+end per contact) can be added to the same file later without breaking this one.

Verdict meanings: `true_contact` (real weight-bearing ground contact), `false_positive` (the detector fired but this is swing/recovery phase, not contact), `inconclusive` (genuinely can't tell from this footage - record why in `reasoning`), `unusable` (occlusion, tracking failure, or other technical problem with this specific window, unrelated to the detection question).

## Consent — read this before adding any clip

Every `manifest.json` entry **must** have a fully populated `consent` block before the clip is used for anything beyond the recorded athlete's own personal review. This is a hard rule, not a suggestion — this platform already has a documented, unresolved concern about handling data from apparent minors (`docs/ENGINEERING_HANDOFF.md` §17.6/§17.7), and a research dataset of real athletes' movement is exactly the kind of data that concern applies to.

- If the athlete is a minor, `consent_type` must reflect guardian consent, not self-consent, and `recorded_by` must be a real, named person accountable for having obtained it.
- `model_training_opt_in` is tracked **separately** from basic research-use consent — never assume it, always ask it as its own question, and default it to `false` unless it was explicitly and separately granted.
- Use a pseudonym in `athlete.pseudonym`, never a real name, in this file (which is checked into git).

This directory does not implement a consent-management *system* (recording/revoking/auditing consent at scale is separate, larger, deferred product work — see the coach/academy connection model's own guardian-consent notes in `docs/ENGINEERING_HANDOFF.md` §18 for where that would eventually live). This is just the metadata field and the process rule for this dataset specifically. If you don't have clear consent, don't add the clip.
