# Next-Session Handoff

**Purpose**: let a brand-new Claude session (zero chat history) resume this project safely. Read this document fully, then read `docs/ENGINEERING_HANDOFF.md` (§25 onward covers everything referenced here, §34 is the most recent) and `docs/DESIGN_BIBLE.md` (the durable product/UX reference). This file is a snapshot as of the moment it was written - re-verify anything load-bearing (git log, test counts) before acting on it, per this project's own "never trust silence, verify current state" convention.

---

## Repository state

- **Branch**: `main`
- **Latest commit**: `84cbed4` (`feat(metrics): introduce canonical metric registry and comparison semantics`)
- **Pushed status**: `origin/main` is at `84cbed4` too - fully pushed, nothing local-only.
- **Working tree**: clean except this file itself and `docs/DESIGN_BIBLE.md` (new), both from this session's documentation pass.
- **Starting the stack locally** (three separate processes, all needed together for the frontend's live analysis flow to work end-to-end):
  1. `cd backend && ./.venv-rtmpose/Scripts/python.exe -m uvicorn rtmpose_worker.app:app --port 8011` - GPU worker. Wait for `GET /health` to show `"initialized": true` (first `/initialize` call is slow, cold).
  2. `cd backend && ./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000` - main API.
  3. `cd frontend && npm run dev` - Vite dev server, port 5173 by default. **If port 5173 is already held by a stray `node.exe` running `vite.js` for this same project** (a leftover from a prior session's preview server that didn't shut down cleanly), it's safe to kill that process and retry - confirmed this exact scenario once already this session.
  - Tests: `cd backend && ./.venv/Scripts/python.exe -m pytest` (no args needed) · `cd frontend && npm run test -- --run` and `npx tsc -b --force` and `npm run lint`.

---

## What happened this session (two very different phases)

### Phase A - Canonical Metric Registry (engineering, shipped)

Fixed two real bugs: `PartnerCompare.tsx` was highlighting a false "winner" for every metric including joint angles (no better/worse direction exists for a joint angle), and the Digital Twin was generating "Improving Left Knee Angle" strengths/personal-bests from the same non-directional metrics. Built one canonical `metricRegistry.ts` with a `comparisonMode` per metric that every consumer now reads instead of assuming "higher is better." Full detail: `docs/ENGINEERING_HANDOFF.md` §33. Shipped in commit `84cbed4`, currently the tip of `main`, already pushed.

### Phase B - Full product/UX/design pass (documentation only, not shipped)

The project owner shifted to product/design work: a full UX audit, four sequential approved planning documents, and a first real wireframe design deliverable for the athlete flow (Landing → Authentication → Onboarding → Home → Upload Flow → Upload Review → Analysis Waiting → Sprint Report → My Progress). **No application code was changed in this phase.** Full detail and the durable, condensed version of every decision: `docs/DESIGN_BIBLE.md`. Session log: `docs/ENGINEERING_HANDOFF.md` §34.

**The single most important thing this phase found**: the public marketing homepage (`/`, viewed while signed out) fabricates metrics and capabilities that don't exist anywhere in the real backend - invented numbers like "Stride Angle: 168°," "Form Score: 8.7/10," and false claims that Hurdles/Long Jump/High Jump have working biomechanics (they don't - Sprint only). This was found, not fixed. See `docs/DESIGN_BIBLE.md` §9 for exact detail and where to look in the frontend.

---

## Test status (re-verify before trusting)

| Suite | Count | Notes |
|---|---|---|
| Backend (`pytest`) | **342 passed** | Unchanged this session - Phase A touched zero backend files, Phase B touched none either. |
| Frontend (`vitest`) | **163 passed** | Up from 123 - Phase A added `metricRegistry.test.ts` (22 tests), extended `twinEngine.test.ts` (+19), added `PartnerCompare.test.tsx` (7). Phase B added no tests (documentation only). |
| TypeScript (`tsc -b --force`) | **Clean** | Zero errors. |
| Lint (`oxlint`) | **8 warnings, all pre-existing** | Same exact list as every prior session - see `docs/ENGINEERING_HANDOFF.md` §33 verification for the file:line list. Zero new warnings. |

---

## Live QA test data (real Supabase rows, disposable, marked)

- `shakti.qa.coach@example.com` - existing QA coach, now connected to **two** athletes (was one before this session).
- `shakti.qa.athlete@example.com` - existing QA athlete, 2 completed sessions (both biomechanics-skipped - no available clip clears the live gate, unchanged finding).
- `shakti.qa.athlete2@example.com` / password `ShaktiQA2Test!2026` - **created this session** to test the two-athlete Coach Compare flow live. One real completed session (biomechanics-skipped).
- All QA-created rows are marked `[QA VERIFICATION] ... safe to delete` in their `notes` fields. Do not delete without checking whether a future session still needs them for live verification.
- **Still true, reconfirmed again this session**: no clip in `backend/examples/` clears the live `biomechanics_ready` gate. Do not fabricate a "completed" biomechanics result to work around this - explicitly rejected precedent, recorded in `docs/DESIGN_BIBLE.md` §10.

---

## Deferred work (unchanged from before this session, still open, still not to be picked up opportunistically)

- **A.** Recalibrate `geometry_stability_score` (needs a larger real-clip dataset).
- **B.** Investigate `stride_velocity_bridge.py`'s left/right progression asymmetry.
- **C.** Independently repair sprint-phase detection's false long-deceleration behavior.
- Promoting one or more of the metric registry's 10 `hidden` entries (tracking confidence, visibility breakdown, camera/lighting/sharpness/frame-rate scores) if the product wants them surfaced.
- The real coach/academy verification workflow (still fully manual).
- Terms/Privacy - explicitly parked, do not pick up unprompted.

---

## Explicit scoping decision (this session)

Work focuses on the **entire platform plus Sprint only** for now. Hurdles/Long Jump/High Jump are deliberately deferred until Sprint mechanics is "top-notch" - do not build or validate anything for those three events opportunistically. This does not reduce the urgency of correcting the homepage's *claim* that those events already have working metrics (see below) - only the urgency of building the real thing for them.

## Recommended next milestone

**Fix the marketing homepage** (`docs/DESIGN_BIBLE.md` §9, §9.1, §9.2 - read all three) - the leading candidate, since it's a live, user-facing violation of the project's own "never invent certainty" guardrail, on the single most-seen page in the product. Per this session's per-metric classification, this splits into two genuinely different pieces of work:
1. **Remove/replace what can never be real, immediately, regardless of anything else**: "Form Score: 8.7/10," the qualitative tiers ("Elite"/"Balanced"/"Excellent"), the "AI Score: 8.9" mockup, and the false "Hurdles: 13 / Long Jump: 9 / High Jump: 10 metrics measured" counts (zero are real). None of these require new science to fix - they require removing a false claim.
2. **Separately scope, as its own audit-and-approve pass**, the Sprint metrics that are genuinely achievable (Stride Angle, arm symmetry, torso lean, real knee-lift/hip-extension framing - all moderate effort, building on the existing pose/angle infrastructure; Top Speed/Acceleration - significant effort, blocked on camera calibration the system doesn't have today).

The next-most-natural alternative, per the project owner's own stated sequencing: continue the design work into the **coach, parent, and scout flows** (the athlete flow is now done - the project owner was explicit about doing "one flow at a time").

A third option, if the project owner wants to move from design into implementation: start building the athlete flow's Phase 1 items from the UI/UX Blueprint's own roadmap (remove the required upload title field, add real upload progress, apply the four-beat error formula platform-wide, lead Sprint Report with a plain-language headline, tie Analysis Waiting to real backend status) - the design trail for exactly this work is unusually complete (`docs/DESIGN_BIBLE.md` + six linked Artifacts).

**None of these were started this session beyond the audit/design/classification work itself.** Follow this repo's own standing workflow for whichever is chosen: audit → proposed plan → project-owner approval → implementation.

---

## Copy-paste prompt for the new session

```
Before doing anything else:

1. Read docs/ENGINEERING_HANDOFF.md in full, paying particular attention to
   §4.11's subsystem classification table and §33-§34 for the most recent
   work.
2. Read docs/DESIGN_BIBLE.md in full - this is the durable, approved
   product/UX/design reference (voice, tone, design tokens, principles,
   guardrails) produced in the previous session. Treat it as product law
   unless the project owner says otherwise.
3. Read docs/NEXT_SESSION_HANDOFF.md in full (this file).
4. Run `git log --oneline -10` and `git status` and confirm they match what
   this file claims - if they don't match, trust the live repo state and
   tell the project owner what's different before proceeding.
5. Run the full backend test suite (`cd backend &&
   ./.venv/Scripts/python.exe -m pytest`) and the full frontend suite
   (`cd frontend && npm run test -- --run`, `npx tsc -b --force`,
   `npm run lint`) and confirm the counts match this file (342 backend,
   163 frontend, tsc clean, 8 pre-existing lint warnings only).
6. Ask the project owner which of the three options in this file's
   "Recommended next milestone" section they want - do not assume, and do
   not start implementation work until a plan is proposed and approved.
```
