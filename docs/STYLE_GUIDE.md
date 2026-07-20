# Shakti Sports AI — Style Guide

**Status: durable reference, split out of `DESIGN_BIBLE.md` §4 once the token system, typography rules, and a real shared component library all existed to document together.** Check this file before writing any new UI. `DESIGN_BIBLE.md` remains the source of truth for product philosophy, voice, and the fifteen immutable design principles (§5 there) — this file is the practical "what class do I actually reach for" reference.

Source of truth for every value below: `frontend/src/index.css` (the `@theme` block) and `frontend/src/components/ui/`. If this doc and the code ever disagree, the code wins — fix this doc.

---

## 1. Color tokens

No component may hardcode a hex value or reach for a raw Tailwind color utility (`orange-600`, `gray-200`, `blue-100`, etc.) directly. Every color is one of the semantic tokens below, each auto-generating `bg-`, `text-`, and `border-` prefixed utilities (Tailwind v4 `@theme` mechanism — see the comment block at the top of `index.css` for how this makes a future dark/high-contrast theme a variable-file edit, not a rewrite).

| Token family | Utility names | Meaning — use for | Never use for |
|---|---|---|---|
| `brand-action` | (base) `#F0600E`, `-hover` `#D94F08`, `-soft` `#FFF4ED`, `-tint` `#FFF8F3`, `-ink` `#7A3006` | Primary buttons, record/upload, active nav, primary links, selected states, focus rings. The one and only brand orange. | Anything routine or decorative — spend it deliberately. |
| `success-progress` | (base) `#16A34A`, `-hover` `#15803D`, `-soft` `#DCFCE7`, `-tint` `#F0FDF4` | Personal best, goal completed, positive trend, an "Excellent" rating. Must feel earned. | Primary navigation or primary CTAs — green celebrates, it never leads. |
| `info-insight` | (base) `#2563EB`, `-hover` `#1D4ED8`, `-soft` `#DBEAFE`, `-tint` `#EFF6FF` | AI explanations, educational content, neutral notifications, in-progress status. | A status judgment of any kind on its own — see the rating-badge exception below for the one deliberate case where it *is* used as one. |
| `warning-attention` | (base) `#D97706`, `-soft` `#FEF3C7`, `-tint` `#FFFBEB` | Needs attention, not failure: recording quality could improve, experimental metric, waiting/processing. | Framing something as broken — that's red's job. |
| `error-failure` | (base) `#DC2626`, `-hover` `#B91C1C`, `-soft` `#FEE2E2` | Something genuinely, technically failed: upload failed, video corrupted, permission denied. | A low score or "poor" performance/recording quality — never a rating, see below for the one exception. |
| `rating-fair` | (base) `#EAB308`, `-soft` `#FEF9C3` | The one genuinely new hue needed for the four-tier rating badge's "Fair" tier (see §3). | Anything outside that one badge. |
| `surface-canvas` / `surface-sunken` / `surface-card` | `#FAFAF7` / `#FFF8F3` / `#FFFFFF` | Three deliberately distinct neutrals: `canvas` = outermost page background, `sunken` = a recessed/tinted section, `card` = a pure-white elevated element. | Collapsing all three to "just white" — they're intentional roles. |
| `border-default` / `border-divider` | `#E5E7EB` / `#F1F5F9` | Structural borders / internal dividers respectively. | — |
| `text-primary` / `text-secondary` / `text-muted` / `text-disabled` | `#111827` / `#374151` / `#6B7280` / `#9CA3AF` | Decreasing emphasis, in that order. | — |
| `category-recording-quality` | `#2f5a6b` | One narrow, deliberate category marker — `TwinProgress.tsx`'s "Recording Quality Trends," distinct from brand-orange "Athletic Performance Trends." | Any other purpose — this is a one-off, not a sixth general-purpose role. |

**Not yet implemented**: a dedicated `confidence.*` token family (low/building/established, monochrome-to-brand progression, never a red/amber/green stoplight) for the My Progress confidence signal — that surface still reuses `success-progress`/`warning-attention`.

### 1.1 The rating-badge exception — read before touching any status color

`RatingBadge` (`PerformanceDetail.tsx`, shared by `AthleteHome.tsx`, `AthleteReports.tsx`, `TwinSessionCard.tsx`, `PartnerCompare.tsx`) gives its four tiers four *distinct* colors instead of the usual two-shades-of-green-and-amber pattern:

| Rating | Variant | Color |
|---|---|---|
| Excellent | `success` | green — unchanged from the general rule |
| Good | `info` | blue |
| Fair | `fair` | yellow (`rating-fair`) |
| Poor | `error` | red |

This is a **deliberate, explicit exception** to "blue/red are never a status judgment," made by the project owner after reviewing a reference mockup. It is scoped to this one badge. Do not generalize it to any other status/quality surface without the same explicit sign-off — everywhere else, the original rule (ratings/quality are never red or blue) still applies.

### 1.2 The dark-mockup exception

A handful of marketing components embed a deliberately dark "device screen" illustration inside an otherwise light page — `EventPreview.tsx` (recording-preview mockup), `CoachTalentSection.tsx`'s Coach Dashboard card, `AIPerformanceAnalysis.tsx`'s Movement Intelligence panel, `AthleteJourney.tsx`'s Athlete Profile card. These are not a themed surface; they're a fixed decorative illustration regardless of site theme, and none of the light-mode tokens above apply to their near-black background or their light-on-dark accent shades (`orange-400`, `green-300`, `white/10`, etc. — none of which have a light-mode token equivalent).

**The rule for these**: leave the decorative dark colors raw. Tokenize only (a) the outer border/shadow where the component meets the real (light) page background, and (b) any spot using the *exact* brand hex `#F0600E` (→ `brand-action`), since that applies regardless of context. Same treatment as the pre-existing modal-scrim overlay (`bg-gray-950/40 backdrop-blur-sm`) in both `AthleteLayout.tsx` and `PartnerLayout.tsx`, which has never been tokenized for the same reason.

---

## 2. Typography

Three typefaces, each confined to a specific role — never mixed within the same text element.

| Typeface | Role | Where |
|---|---|---|
| **Lexend** | Every in-product UI/body/heading, sitewide default (`--font-sans` in `index.css`) | Everywhere except `Logo.tsx` (see below). Switched from Inter — the one major Google Font engineered against reading-research data to improve reading speed and reduce visual stress for developing readers, matching this product's grade 4–6 reading-level bar (see `DESIGN_BIBLE.md` §2). |
| **Anton** | The logo wordmark only | `Logo.tsx` — the sole remaining use, a logo isn't body copy. Every former use (`Hero.tsx`, `FinalCTA.tsx`, the rest of the marketing pages, all of Auth/onboarding) migrated to Lexend in the session that removed Anton sitewide except the logo. Anton's `@font-face` (see below) still loads for this one reason — do not drop it while `Logo.tsx` uses it. |
| **JetBrains Mono** | Compact labels, mono data, identifiers, badges — never body prose | Widely used sitewide (session IDs, stat values, uppercase eyebrow labels, badge text). Applied via arbitrary `font-['JetBrains_Mono']` classes at each call site — not yet tokenized (see §5, "not yet migrated"). |

**Fonts are self-hosted, not loaded from Google Fonts.** All 11 weight/family files live in `frontend/src/assets/fonts/` (Latin subset only, matching this site's English-only content) and are declared as `@font-face` rules at the top of `index.css` — Anton 400; Lexend 300/400/500/600/700/900; JetBrains Mono 400/500/600/700. This weight set was deliberately corrected against actual usage (`grep`'d Tailwind `font-*` weight utilities), not copied from the old Google Fonts request — it drops Lexend 800 (never used) and adds Lexend 900 and JetBrains Mono 700 (both used, e.g. `font-black` ratings/avatars and bold mono labels — previously silently faux-bolded by the browser since those weights were never loaded). If you introduce a new `font-*` weight utility on Lexend or JetBrains Mono anywhere, check it against this list — an unlisted weight falls back to browser-synthesized bold/thin, which looks worse than the real thing.

**Anton is used nowhere except `Logo.tsx`'s wordmark.** Every screen — Marketing, Auth/onboarding, the Athlete Console, the Partner Console — is Lexend. If you're writing a heading, it's Lexend — `text-2xl font-bold ... md:text-3xl` for a page `h1`, `text-xl font-bold` for a section `h2`, `text-lg font-bold` for a card title, dropping `uppercase` wherever the underlying text is natural-case (the convention already applied across every migrated screen — don't invent a new one per page). Hero-scale or card-scale display statements — `Hero.tsx`'s headline, `FinalCTA.tsx`'s closing line, the large two-line intro headlines on each home-page section, `RoleCard.tsx`'s title — size up from that base by context rather than following the h1/h2 rule by rote; check the file itself for the current size rather than assuming.

---

## 3. The component library

`frontend/src/components/ui/` — reach for these before hand-rolling a new `<div className="rounded-2xl border ...">`. Each was extracted from a real pattern that had already been copy-pasted 2–5 times across the codebase.

### `Badge`
```tsx
<Badge variant="success" size="chip">Excellent Recording</Badge>
```
- `variant`: `success` / `info` / `warning` / `fair` / `error` / `neutral` / `brand`
- `size`: `pill` (marketing badge shape, rounded-full, the default) / `chip` (compact mono/uppercase, used for Athlete Console rating and status badges)
- Default (`success`/`pill`) is byte-identical to this component's pre-token-system look — `Hero.tsx`'s "Built for the road to LA 2028" badge needed zero changes.
- `success` has a subtly different text shade at `chip` size than at `pill` size (see the code comment in `Badge.tsx`) — this is intentional, not a bug, kept because both shades were already independently verified correct before being unified into one component.

### `Button`
```tsx
<Button variant="primary">Upload your first clip</Button>
<Button variant="link">View full report</Button>
```
- `variant`: `primary` (brand-action solid) / `secondary` (green solid, no current consumer) / `outline` (bordered, neutral) / `link` (text-only, no box)
- `primary`/`outline` are Hero.tsx/FinalCTA.tsx's marketing CTAs, now on-token. `secondary` is tokenized for consistency but has zero real usage anywhere today.

### `StatTile`
```tsx
<StatTile icon={Activity} value={15} label="Total sessions" tone="brand" />
```
Icon-in-soft-circle + mono value + label. `tone`: `brand` / `info` / `success` (colors the icon's circle badge). Extracted from the Performance Summary card on Athlete Home.

### `RailCard`
```tsx
<RailCard tone="sunken">...</RailCard>
```
The `rounded-2xl border border-border-default p-5` wrapper used by every rail card on Athlete Home. `tone`: `card` (white, default) / `sunken` (warm-tinted, for "highlighted" cards like Personal Best/Current Goal).

### `IconButton`
```tsx
<IconButton icon={Upload} label="Upload a performance" to={ROUTES.ATHLETE.NEW_PERFORMANCE} />
<IconButton icon={Bell} label="Notifications" onClick={...} hasIndicator={hasNotifications} ariaExpanded={open} />
```
Renders a `Link` when `to` is passed, a `<button>` otherwise. `hasIndicator` shows a small dot (real unread state only, never decorative). Used for the Athlete Console navbar's Upload/Notifications/mobile-menu-toggle buttons — **not yet adopted by Partner Console**, which deliberately kept its own orange-hover treatment on equivalent buttons rather than silently switching to `IconButton`'s neutral hover (a real, undiscussed visual behavior change — see the code comment in `PartnerLayout.tsx`).

---

## 4. Migration status (re-verify before trusting — this is a snapshot)

**Fully on tokens** (colors + confirmed Anton/Lexend placement): `index.css`, the whole `components/ui/` library, `AthleteLayout.tsx`, `AthleteHome.tsx`, `PerformanceDetail.tsx`'s `RatingBadge` only, the entire Auth/onboarding feature, the entire Partner Console (`PartnerLayout.tsx` + all 10 `Partner*.tsx` pages), and the entire Marketing surface (`About`, `Contact`, `Mission`, `NotFound`, `ComingSoon`, all of `home/`).

**Not yet migrated** (still raw Tailwind colors and/or hex, confirmed by a full sitewide sweep this session): `PerformanceDetail.tsx`'s other sections (`AnalysisReport`, `MetricCard`, `ConfidenceGauge`, `SegmentCard`, the comparison table, the page shell itself — only its `RatingBadge` got migrated), `AthleteCoaches.tsx`, `AthleteGoals.tsx`, `AthleteProfile.tsx`, `AthleteReports.tsx`, `AthleteSettings.tsx`, `DigitalTwin.tsx`, `WizardLayout.tsx`, every `Twin*.tsx` component, `PerformanceHistory.tsx`, `PerformanceProcessing.tsx`, the wizard steps (`DetailsStep`, `EventStep`, `PerformanceTypeStep`, `ReviewStep`, `UploadStep`), and shared chrome (`Navbar.tsx`, `Footer.tsx`, `UserMenu.tsx`, `EmptyState.tsx`, `Logo.tsx`, `AuthLayout.tsx`, `HomePage.tsx`, `ProtectedRoute.tsx`, `RequireNoRole.tsx`, `RoleGate.tsx`, `readinessTrend.tsx`). These Anton-migrated in an earlier session (§35.4 of `ENGINEERING_HANDOFF.md`) but were never brought onto the color-token system.

If you're about to touch any file in that second list for an unrelated reason, migrating its colors while you're in there is in scope and welcome — just disclose it, same as every other batch in this history.

---

## 5. The rest of the rulebook

These live in `DESIGN_BIBLE.md`, not duplicated here — check that file for: the fifteen immutable design principles (§5), the four-beat error copy formula and progressive-disclosure model (§2–3), the guardrails on never inventing certainty (§6), and the full decision log (§7).
