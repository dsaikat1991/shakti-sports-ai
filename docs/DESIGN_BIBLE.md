# Shakti Sports AI — Product & Design Bible

**Status: approved product law, condensed from six full design documents produced in a single session (see "Full documents" below for the live, richly-formatted originals). This file exists so the decisions survive even if the original Artifact links become unreachable — treat this markdown as the durable source of truth and the Artifacts as the illustrated edition.**

Read this before making any frontend UX/copy/visual decision. It does not cover backend/pipeline engineering (see `ENGINEERING_HANDOFF.md`).

---

## 0. The one-sentence mission

*"Discover talent by performance, not by geography."* An 8-year-old in a village and an Olympic scout use the same product, see the same honest data, at different altitudes of detail — never a different truth.

## 1. Core philosophy

The product is **not an AI analytics dashboard. It is an AI-powered athletics coach.** The technology should disappear; the coaching should remain. Seven traits it answers to: honest, warm, athletic, human, clear, encouraging, trustworthy. Never corporate, never intimidating, never cluttered.

**The one rule that overrides every other rule in this document**: *simple must never mean untrue.* Simplifying language must never mean fabricating confidence, hiding a real limitation, or implying more certainty than the data earns. This protects the platform's single most valuable, already-real asset: it never invents a confidence number and always labels experimental metrics as experimental.

## 2. Voice & copy rules

- Reading level: grade 4–6 for anything a first-time or young user sees by default. One idea per sentence, sentences under ~15 words, no bare technical nouns ("confidence," "variation") without a plain meaning attached in the same breath, no number shown without what it means for the reader.
- **Four-beat error formula**, applied everywhere, no exceptions: (1) what happened, plainly (2) why, only if it helps (3) what to do next, specific and doable (4) reassurance that this is normal and fixable. Never show a raw system/network error string to a user.
- Tone by moment: success = specific and earned, never generic; struggle/error = calm and forward-looking, never blaming; waiting = honest about real status, never a performance; data = plain meaning leads, the number follows.
- **The "same fact, four altitudes" worked example** (the whole progressive-disclosure philosophy in one case): a session's camera was held too low.
  - *Athlete*: "We couldn't read your run this time — the camera was a little low. Try holding it around waist height next time! 📷"
  - *Parent*: "This session's movement analysis isn't ready yet — a small camera adjustment next time will fix it. Nothing to worry about."
  - *Coach*: "Camera height failed the check (30/100, need 60+). Movement data unavailable this session — worth a re-shoot."
  - *Scout*: "camera_height_score: 30.0 (threshold 60.0) — biomechanics_ready: false. Re-shoot required for kinematic data."
  Same truth, four altitudes — nothing hidden, nothing invented, just more or less detail depending on who's asking.

## 3. Progressive disclosure — one platform, four experiences

| Audience | Real question | Default view |
|---|---|---|
| Beginner/athlete (often a child) | "What should I do next?" | One headline, one action |
| Parent | "Is my child okay and improving?" | One reassuring line |
| Coach | "Who needs my attention today?" | Roster/triage list, not pairwise comparison |
| Scout/elite | "Is this data trustworthy, how does it compare?" | Full statistical detail, by default |

Nothing is ever hidden as a secret — always revealed progressively (a beginner can tap "show me more"; a scout can collapse to simple).

## 4. Design tokens — **implemented** as of the session that shipped commit `eed5a0b` (superseding the original proposal below `§4.0`)

**Status: this is no longer a proposal — it is live in `frontend/src/index.css` via a Tailwind v4 `@theme` block, and is the durable reference for every color decision from here on.** Full engineering detail (mechanism, bugs found/fixed, migration scope so far): `ENGINEERING_HANDOFF.md` §35.3. This section states the settled rule; that section explains how it was built.

**The rule, no exceptions**: no component may hardcode a hex value. No component may reach for a raw Tailwind color utility (`orange-600`, `green-500`, `blue-700`, `gray-200`, etc.) directly. Every color reference is one of the semantic classes below. If a screen needs a color and none of these fit, that's a sign a real new semantic role is missing — propose a new token, don't reach for a raw utility as a shortcut.

| Token family | Utility names (bg-/text-/border- + suffix) | Meaning — use for | Never use for |
|---|---|---|---|
| `brand-action` | (base), `-hover`, `-soft`, `-tint`, `-ink` | Primary buttons, record/upload, active nav, primary links, selected states, focus rings. Orange = action/courage/effort. | Anything routine or decorative — spend it deliberately. |
| `success-progress` | (base), `-hover`, `-soft`, `-tint` | Personal best, goal completed, achievement, positive trend, a "Good"/"Excellent" performance rating. Green = progress/achievement, must feel earned. | Primary navigation or primary CTAs — green never leads, it celebrates. |
| `info-insight` | (base), `-hover`, `-soft`, `-tint` | AI explanations, educational content, coach insights, neutral notifications, help/documentation. Blue = knowledge/trust/precision. | A status judgment of any kind — a quality rating or performance grade is never "insight" blue. |
| `warning-attention` | (base), `-soft`, `-tint` | Needs attention, not failure: recording quality could improve, an experimental metric, waiting/processing, a "Fair"/"Poor" performance rating. | Framing something as broken — that's red's job, not amber's. |
| `error-failure` | (base), `-hover`, `-soft` | Something genuinely, technically failed: upload failed, video corrupted, analysis crashed, permission denied. | A low score, a skipped analysis, or "poor" performance/recording quality — none of those are failures. |
| `surface-canvas` / `surface-sunken` / `surface-card` | (base only) | Three deliberately distinct neutrals: `canvas` = outermost page background, `sunken` = a recessed/tinted section within the page, `card` = a pure-white elevated element. | Collapsing all three to one "just make it white" — they're intentional roles, not accidental drift (an earlier pass in this project's history proposed collapsing them; superseded). |
| `border-default` / `border-divider` | (base only) | Structural borders and internal dividers respectively. | — |
| `text-primary` / `text-secondary` / `text-muted` / `text-disabled` | (base only) | Decreasing emphasis, in that order. | — |
| `category-recording-quality` | (base only) | A narrow, deliberate category marker distinct from the five roles above — e.g. "Recording Quality Trends" must never read as the same kind of observation as "Athletic Performance Trends." | Any other purpose — this is a one-off, not a general-purpose sixth color. |
| `rating-fair` | (base), `-soft` | **Deliberate, disclosed exception, see below.** The one genuinely new hue (yellow) needed for the four-tier performance-rating badge (Excellent/Good/Fair/Poor). | Anything outside that one badge. |

**Performance-rating badge — four distinct colors, a deliberate exception to the rule above** (project owner's explicit instruction, session after `eed5a0b`): `RatingBadge` (`PerformanceDetail.tsx`, shared by `AthleteHome.tsx`/`AthleteReports.tsx`/`TwinSessionCard.tsx`/`PartnerCompare.tsx`) now maps Excellent → `success-progress` (green, unchanged), Good → `info-insight` (blue), Fair → the new `rating-fair` (yellow), Poor → `error-failure` (red). This intentionally overrides this file's own general rule that blue/red are never a status judgment on a rating — narrowly scoped to this one badge component, by explicit direction, not a general license to reuse `info-insight`/`error-failure` for other quality/status surfaces. Any other screen still follows the original rule (ratings/quality never red or blue) unless it gets the same explicit sign-off.

**Not yet implemented, still open**: a dedicated `confidence.*` token family (low/building/established, monochrome-to-brand progression, never a red/amber/green stoplight) for the Digital Twin/My Progress confidence signal specifically — that surface still reuses `success-progress`/`warning-attention` rather than having its own dedicated name. Revisit if/when that surface needs to evolve independently.

**Typography — implemented for the Athlete Console, not yet elsewhere**: Anton confined to Landing's hero (plus `Logo.tsx`, a second sanctioned exception for the brand wordmark specifically); Lexend carries every in-product headline (switched from Inter this session — chosen for its reading-research-backed legibility, matching this product's grade 4–6 reading-level bar). Migrated so far: Athlete Console (all screens). **Not yet migrated**: Auth/onboarding, the entire Coach/Academy Console, marketing pages other than the Landing hero itself. See `ENGINEERING_HANDOFF.md` §35.8 for the exact remaining scope — this is the project owner's stated next priority, ahead of any other work.

**Dark mode**: ship later, not now, not never. Justification: the bigger unaddressed need is legibility in *bright outdoor sunlight* (the real filming environment), which dark mode doesn't help. The token architecture above already satisfies "a future token-file edit, not a rewrite" — Tailwind v4's generated utilities reference the CSS variable itself, not a baked-in literal, so a future `[data-theme="dark"] { --color-surface-canvas: ...; }` override repaints every consuming component automatically. Confirmed working, not just architected — see `ENGINEERING_HANDOFF.md` §35.3.

### 4.0 Original proposal (superseded by the table above, kept for history)

**Keep unchanged**: brand accent `#F0600E` (the one and only brand color — do not add a second "brand" hue), and the Anton/Inter/JetBrains Mono trio.

**Fix**: Anton is currently misused on real instructional headings (hurts readability) — it should be confined to Landing's hero only, never inside the authenticated product. Inter carries every in-product headline, including Sprint Report/My Progress "big statement" text.

## 5. Fifteen immutable design principles

1. One screen. One job. 2. Meaning before metrics. 3. Coach before software. 4. Simple must never mean untrue. 5. Motion teaches, or it doesn't happen. 6. Confidence is not certainty — never color them the same. 7. Every number must answer "so what?" before it earns a place on screen. 8. One brand color, spent deliberately. 9. Borders explain structure; shadows are earned, not default. 10. Icons for recognition, illustrations for teaching, words for truth. 11. Round says "welcome"; sharp says "precise" — choose on purpose. 12. Nothing is red unless something genuinely broke. 13. The phone is the whole design; the desktop is a bigger room, not a shrunken one in reverse. 14. Every token has one job, so dark mode is a future edit, not a future rewrite. 15. If a decision can't be explained to an 11-year-old, it isn't ready to ship.

## 6. Things we will never do (guardrails)

Never invent certainty. Never exaggerate what the AI can currently do. Never shame an athlete for a low score, a skipped analysis, or a bad video. Never hide uncertainty to make a screen look cleaner. Never use fear, guilt, or manufactured urgency to drive engagement. Never show a beginner a technical term before they need it. Never treat a low-confidence or experimental measurement as validated. Never optimize time-in-app over honesty. Never make an irreversible action easy to trigger by accident. Never require literacy in one language to complete a core action. Never let a coach/scout's need for detail leak into a beginner's default view. Never treat "not enough data yet" as a failure rather than a normal beginning.

## 7. Approved product decisions (permanent log — do not re-litigate without a reason)

| Decision | Reason | Status |
|---|---|---|
| Rename "Digital Twin" → "My Progress" | Jargon → the athlete's own question, in their own words | **Approved & built** — nav label/icon and Athlete Console copy updated (commit `eed5a0b`); route path and internal identifiers unchanged |
| Coach Dashboard becomes roster/triage-first | A coach's real daily question is "who needs me," not pairwise comparison | Approved, not built |
| Athlete Compare demoted to secondary nav | Narrower job than daily triage; primary placement overstates its role | Approved, not built |
| No AI mascot/named character | A cartoon invites gimmick logic that competes with quickly telling the truth | Approved |
| Cadence/stride frequency stay `HIGHER_IS_BETTER` | Matches existing, already-shipped, test-locked behavior; disclosed via limitation text, not asserted as validated science | **Approved & implemented** (commit `84cbed4`) |
| Joint angles stay `NEUTRAL` | No honest bigger/smaller-is-better direction exists | **Approved & implemented** |
| Onboarding profile completeness deferred past first upload | Get to a first result in under a minute | Approved, not built |
| Parent given a first-class, separate role/view | A parent's question differs in kind from an athlete's or coach's | Approved, not built |

## 8. Full documents (the illustrated editions — verify these links still resolve before relying on them)

1. UX & Product Review — `https://claude.ai/code/artifact/c80e588e-77b7-4178-94c7-c1c29e0f7b10`
2. Product Experience Bible — `https://claude.ai/code/artifact/16dee32b-d15c-4340-bf62-36244d774850`
3. Product Experience Specification v1.0 — `https://claude.ai/code/artifact/a93f6991-33ba-49b4-b3d8-d749d3f40d50`
4. UI/UX Blueprint v1.0 — `https://claude.ai/code/artifact/61b154e8-f44e-4f82-a6c9-363af04651a3`
5. Design System v1.0 — `https://claude.ai/code/artifact/18891a89-7522-4bb6-aac7-2d57f36bf98c`
6. Athlete Flow — ASCII wireframes (exploratory pass) — `https://claude.ai/code/artifact/54dfdf13-a5ea-45d4-bcb6-c447f6850aef`
7. Athlete Flow — first real design deliverable (traced to UX Review + Bible) — `https://claude.ai/code/artifact/ae1b5822-d0fb-4d4c-90a7-b80672db9328`

These are Claude Artifacts (private to the account that generated them) — if a future session can't reach them, this markdown file is the fallback source of truth; regenerate the illustrated versions only if actually needed for a visual handoff.

## 9. Critical, unresolved finding from live testing (verified in a real browser, this session)

**The public marketing homepage fabricates capabilities and metrics that do not exist in the real product**, and this is more urgent than any in-app copy work above. Confirmed by direct navigation to `http://localhost:5173/` while signed out:

- The hero "live analysis" demo shows **Stride Angle: 168°, Form Score: 8.7/10, Arm Drive: Balanced, Top Speed: 34 km/h, Acceleration: Elite** — none of these are computed anywhere in the real backend. The only real metrics are cadence, stride frequency, knee symmetry, ground contact, duty factor, flight time, and joint angles (see `metricRegistry.ts`).
- It claims **"Hurdles: 13 metrics measured," "Long Jump: 9 metrics measured," "High Jump: 10 metrics measured."** Confirmed repeatedly this session (backend audit + `metricRegistry.ts`'s own comments): biomechanics is implemented for **Sprint only**. These numbers are invented.
- A fictional example athlete shows **"AI Score: 8.9," "Coach Views: 24," "Weekly Progress +14%"** — no such scoring/analytics system exists.

This directly violates guardrail §6 above ("never invent certainty," "never exaggerate what the AI can currently do") — on the single most-seen page in the product, before a user has ever trusted it with anything. **Recommend this be the first fix of the next session**, ahead of any athlete-flow redesign work: either replace the demo with real captured output from an actual analysed clip, or clearly label it as an illustrative mockup, and correct the per-event "metrics measured" counts to match what's actually implemented (Sprint only, today).

Likely file locations to check first: `frontend/src/features/home/` (marketing/landing components — `PerformanceSummary.tsx` was already found this session to contain similar unvalidated copy) and whatever component renders the hero "ANALYZING" panel and the "Aryan Roy" example athlete profile.

### 9.1 Scoping decision: Sprint and the platform first, other events later

**Explicit project-owner decision**: work now focuses on the entire platform plus Sprint specifically. Hurdles, Long Jump, and High Jump are deliberately deferred until Sprint mechanics is "top-notch" - do not build or validate anything for those three events opportunistically alongside Sprint work. This makes the homepage's false "Hurdles: 13 metrics measured / Long Jump: 9 / High Jump: 10" claims lower-urgency to *build toward* (that's a real, multi-month R&D program per event - new camera-angle research, event-specific validation footage, from-scratch biomechanics, not a metrics-add) but no less urgent to *stop claiming* - those specific numbers should be corrected or removed regardless of when the real work happens.

### 9.2 Per-metric classification (Sprint-scoped) - what's real, what's possible, what can never be real

**Already real today** - the homepage just needs to show genuine computed output instead of demo numbers: Cadence, Ground Contact (experimental), Knee Symmetry, Stride Frequency, Flight Time (experimental), Duty Factor (experimental).

**Possible, with real engineering/validation work - not a quick add**:
- *Stride Angle* - undefined today. Needs a sports-science definition (which joint, which moment in the stride) before implementation, then validation against real footage with the same rigor as the existing stride-geometry correction work. Moderate effort - the pose/angle infrastructure it would build on already exists and works.
- *Arm symmetry* (the real version of "Arm Drive") - elbow angles are already tracked; a left/right arm-swing symmetry score is a direct mirror of the existing `knee_symmetry_score` pattern. Low-to-moderate effort.
- *Body lean / torso angle* - computable from existing pose keypoints the same way joint angles are. Low-to-moderate effort.
- *Knee lift, hip extension* (as real numbers, not the vague framing currently shown) - the underlying angle data exists; needs a real definition of what "100%"/"excellent" means, plus validation. Moderate effort.
- *Top Speed* - needs real-world distance calibration from a 2D phone video; the system does **zero** camera calibration today (a reference object, a marked distance, or a disclosed-error fixed assumption like standard track lane width). Significant, genuinely new capability - not an extension of the existing angle work.
- *Acceleration (as a number)* - the derivative of Top Speed once that exists; cheap on top of it, but fully blocked on the same calibration problem.

**Can never be real, regardless of engineering effort**:
- *Form Score: 8.7/10* - an explicitly-described composite of other scores with invented weights. No data exists showing what weighting correlates with real sprint quality; computing it "for real" still means someone picks arbitrary numbers. **The app's own existing copy already reached this conclusion** - its in-app "Coming Soon" note for "Sprint Score" says it needs "real, licensed reference data" before shipping responsibly. The homepage currently contradicts a standard the product already set for itself elsewhere.
- *Qualitative tiers* ("Acceleration: Elite," "Arm Drive: Balanced," "Knee Lift: Excellent") - even once the underlying numbers are real, a tier label needs validated benchmark thresholds, which is the same reference-data problem as Form Score, not more pose-tracking work.
- *"AI Score: 8.9"* on the athlete-profile mockup - same problem as Form Score, a single invented composite for a whole athlete.

**Different category entirely**: "Coach Views" and "Invites" aren't biomechanics claims at all - just usage counters. Trivial to make real (count real events) whenever the product wants that feature; not a science problem.

## 10. Live QA test data (created this session, real Supabase rows, disposable)

- `shakti.qa.coach@example.com` — existing QA coach, connected to 2 athletes.
- `shakti.qa.athlete@example.com` — existing QA athlete, 2 completed sessions (both biomechanics-skipped).
- `shakti.qa.athlete2@example.com` / password `ShaktiQA2Test!2026` — **created this session** specifically to test the two-athlete Coach Compare flow; 1 completed session (biomechanics-skipped, detection 94.35%, readiness 60/100). All rows marked `[QA VERIFICATION] ... safe to delete` in their notes fields.
- **No available real clip clears the live `biomechanics_ready` gate** (confirmed again this session) — closing this gap needs real footage shot correctly (waist-height, side-on, closer framing), not more QA data with the existing three stock clips. Do not fabricate a "completed" biomechanics result to work around this — that was explicitly rejected earlier in this project's history as crossing into fabricating production data.
