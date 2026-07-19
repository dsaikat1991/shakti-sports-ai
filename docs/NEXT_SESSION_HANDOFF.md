# Next-Session Handoff

**Purpose**: let a brand-new Claude session (zero chat history) resume this project safely. Read this document fully, then read `docs/ENGINEERING_HANDOFF.md` (§35 is the most recent section) and `docs/DESIGN_BIBLE.md` (the durable product/UX/design reference — §4 was rewritten this session to reflect what's actually implemented). This file is a snapshot as of the moment it was written - re-verify anything load-bearing (git log, test counts) before acting on it, per this project's own "never trust silence, verify current state" convention.

---

## Repository state

- **Branch**: `main`
- **Latest commit**: `eed5a0b` (`feat(design-system): implement approved Home mockup and sitewide semantic color tokens`)
- **Pushed status**: **NOT pushed** - `origin/main` is still at `9bfbace`. `eed5a0b` and `9bfbace` are both local-only ahead of the remote as of this writing (confirm with `git log origin/main..HEAD`). Do not push without explicit instruction.
- **Working tree**: clean as of the end of this session.
- **Starting the stack locally** (three separate processes, all needed together for the frontend's live analysis flow to work end-to-end):
  1. `cd backend && ./.venv-rtmpose/Scripts/python.exe -m uvicorn rtmpose_worker.app:app --port 8011` - GPU worker. Wait for `GET /health` to show `"initialized": true` (first `/initialize` call is slow, cold).
  2. `cd backend && ./.venv/Scripts/python.exe -m uvicorn app.main:app --port 8000` - main API.
  3. `cd frontend && npm run dev` - Vite dev server, port 5173 by default. **If port 5173 is already held by a stray `node.exe` running `vite.js` for this same project** (a recurring leftover from a prior session's preview server not shutting down cleanly - confirmed multiple times across sessions), it's safe to kill that process and retry.
  - Tests: `cd backend && ./.venv/Scripts/python.exe -m pytest` (no args needed) · `cd frontend && npm run test -- --run` and `npx tsc -b --force` and `npm run lint`.

---

## What happened last session

Two commits shipped, neither pushed:

1. `9bfbace` - athlete-flow Phase 1 (optional upload title, real upload progress, four-beat error formula, plain-language report headline, honest Analysis Waiting status) plus the hybrid session-naming scheme (`performance_type` DB column + personal note, `buildPerformanceDisplayName()`).
2. `eed5a0b` - the Athlete Home screen rebuilt to match an approved Artifact mockup exactly (real data only, honest states), the shared `AthleteLayout.tsx` sidebar/topbar restyled, "Digital Twin" renamed to "My Progress" sitewide, 12 more Athlete Console screens migrated off Anton onto Inter, and - the largest piece - the project owner's official Color Philosophy spec implemented as a centralized semantic design-token system in `frontend/src/index.css` (Tailwind v4 `@theme`), with `AthleteLayout.tsx`, `AthleteHome.tsx`, and `PerformanceDetail.tsx`'s `RatingBadge` migrated onto it.

Full detail: `docs/ENGINEERING_HANDOFF.md` §35. The token table itself, with intended meaning per token: `docs/DESIGN_BIBLE.md` §4 (rewritten this session - the old §4 is now §4.0, kept for history).

**The project owner's explicit stated priority for this next session**: finish/"close" the design constitution and style guide for the entire web app **before** picking up anything else (the marketing-homepage fabricated-metrics fix, the three deferred research items, and the open `performance_type` display question below all stay parked until this is done).

---

## Test status (re-verify before trusting)

| Suite | Count | Notes |
|---|---|---|
| Backend (`pytest`) | **342 passed** | Untouched this session - zero backend files changed (confirmed via `git status backend/`). |
| Frontend (`vitest`) | **179 passed, 11 files** | Up from 163 - added `AthleteHome.test.tsx` (16 tests) and `performanceDisplayName.test.ts` (6 tests, shipped in `9bfbace`). |
| TypeScript (`tsc -b --force`) | **Clean** | Zero errors. |
| Lint (`oxlint`) | **9 warnings, all the same pre-existing pattern** | One new instance (`AthleteHome.tsx:145`, `only-export-components` - from deliberately exporting `deriveHomeHeroState`/`HeroCard` for testability, the same pattern `PerformanceProcessing.tsx`/`PerformanceDetail.tsx`/`AuthContext.tsx` already use). Zero new warning *categories*. |

---

## Live QA test data (real Supabase rows, disposable, marked) - unchanged this session

- `shakti.qa.coach@example.com` - QA coach, connected to two athletes.
- `shakti.qa.athlete@example.com` / `shakti.qa.athlete2@example.com` (password `ShaktiQA2Test!2026`) - QA athletes, all sessions biomechanics-skipped.
- All QA rows marked `[QA VERIFICATION] ... safe to delete` in their `notes` fields.
- **Still true**: no clip in `backend/examples/` clears the live `biomechanics_ready` gate. Do not fabricate a "completed" biomechanics result to work around this.

---

## Open item, not resolved - do not assume either way

The project owner reported seeing rows on their own personal account (`Performance #11`-`#14`) rendering as `Session — "fff"` instead of a real type label. Traced the full write path and found no bug in current code - the likely explanation is these are legacy rows predating the `performance_type` migration (which correctly fall back to `"Session"` by design). **The project owner was asked to create one fresh test performance to confirm and never confirmed back.** Check directly against the live Supabase project (`select performance_type, title, created_at from performances where athlete_id = ... order by created_at desc limit 5`) or ask again before touching `performanceDisplayName.ts` or the insert path. Full detail: `docs/ENGINEERING_HANDOFF.md` §35.7.

---

## Deferred work (unchanged, still open, still not to be picked up opportunistically ahead of the design-system priority below)

- **A.** Recalibrate `geometry_stability_score` (needs a larger real-clip dataset).
- **B.** Investigate `stride_velocity_bridge.py`'s left/right progression asymmetry.
- **C.** Independently repair sprint-phase detection's false long-deceleration behavior.
- The marketing homepage's fabricated metrics (`docs/DESIGN_BIBLE.md` §9) - found and classified two sessions ago, still not fixed. Deliberately deferred behind the design-system close-out below, per the project owner's own explicit sequencing.
- Promoting one or more of the metric registry's 10 `hidden` entries, if the product wants them surfaced.
- The real coach/academy verification workflow (still fully manual).
- Terms/Privacy - explicitly parked, do not pick up unprompted.

---

## Recommended next milestone: close the design constitution and style guide, sitewide

This is the project owner's own explicit instruction, not a suggestion among options. Three concrete pieces, per `docs/ENGINEERING_HANDOFF.md` §35.8:

1. **Anton migration, batches 2-4**: Auth/onboarding screens, the entire Coach/Academy Console (`PartnerLayout.tsx` + every `Partner*.tsx` page), and marketing/public pages. `Hero.tsx` (Landing) is the **only** place Anton should remain anywhere in the app.
2. **Semantic-token migration, sitewide**: every screen outside `AthleteLayout.tsx`/`AthleteHome.tsx`/`PerformanceDetail.tsx`'s `RatingBadge`/`index.css` still has raw Tailwind color utilities and/or hardcoded hex. Audit file-by-file, migrate each onto the token names already defined in `docs/DESIGN_BIBLE.md` §4 / `frontend/src/index.css`. Only add a new token if a screen needs a genuinely distinct semantic role the existing nine families don't cover - not as a shortcut for a one-off color.
3. **Formalize the result as one durable reference** - either substantially expand `docs/DESIGN_BIBLE.md` §4 further, or split a dedicated `docs/STYLE_GUIDE.md` out of it, covering: the full token table with intended meaning (already drafted this session, may need extending as new screens are migrated), the Anton/Inter/JetBrains Mono confinement rule, the Canvas/Surface/Card three-tier neutral system, the rating-badge color rule, and the existing fifteen immutable design principles (`docs/DESIGN_BIBLE.md` §5) - one place to check before writing any new UI.

Standing workflow for this project applies throughout: audit each area file-by-file before changing it, flag anything that ripples beyond a single screen (shared components like `PartnerLayout.tsx` affect every partner-role page at once - confirm before changing), verify via `tsc`/full test suite/lint/live browser check before reporting any batch done, disclose every judgment call rather than silently deciding, and do not commit or push without explicit instruction.

---

## Copy-paste prompt for the new session

```
Before doing anything else:

1. Read docs/ENGINEERING_HANDOFF.md §35 (most recent - Home mockup port,
   sidebar restyle, Digital Twin rename, Anton migration batch 1, and the
   semantic color-token system), and skim §33-34 for the metric-registry
   and design-audit history behind it.
2. Read docs/DESIGN_BIBLE.md in full, especially §4 (the token table - the
   settled rule for every color in the app) and §5 (fifteen immutable
   design principles). Treat this file as product/design law unless the
   project owner says otherwise.
3. Read docs/NEXT_SESSION_HANDOFF.md in full (this file).
4. Run `git log --oneline -5` and `git status` and confirm they match what
   this file claims (latest commit eed5a0b, NOT pushed, clean tree) - if
   they don't match, trust the live repo state and tell the project owner
   what's different before proceeding.
5. Run the full backend test suite (`cd backend &&
   ./.venv/Scripts/python.exe -m pytest`) and the full frontend suite
   (`cd frontend && npm run test -- --run`, `npx tsc -b --force`,
   `npm run lint`) and confirm the counts match this file (342 backend,
   179 frontend/11 files, tsc clean, 9 lint warnings all pre-existing
   pattern).
6. The project owner's explicit priority: close the design constitution
   and style guide for the entire web app before anything else. Propose a
   concrete plan for the three pieces in this file's "Recommended next
   milestone" section (Anton migration batches 2-4, sitewide semantic-
   token migration, formalizing the result as one durable reference
   document) and get it approved before starting implementation - do not
   assume scope or sequencing.
```
