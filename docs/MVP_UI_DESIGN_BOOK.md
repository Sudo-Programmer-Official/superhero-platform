# OpenMat MVP UI Design Book

## 1) Purpose
This document is the UI source of truth for OpenMat MVP surfaces, especially the practitioner app shell under `/app/*`.

Goals:
- Keep UI consumer-grade and mobile-first.
- Reduce cognitive load.
- Keep one obvious primary action per screen.
- Preserve backend capability while simplifying presentation.

Non-goals:
- Rewriting API contracts.
- Replacing legacy dashboard/admin systems.
- Broad visual experiments that break consistency.

## 2) Product Principles
1. `Simple on top, powerful underneath`
- Primary shell should feel lightweight.
- Advanced controls live behind `Advanced Workspace`.

2. `One primary action per screen`
- Every screen has one dominant CTA.
- Secondary actions are visually subordinate.

3. `Mobile-first by default`
- Design for thumb reach, safe areas, and narrow widths first.
- Desktop should be adaptation, not primary source layout.

4. `Progressive disclosure`
- Show essentials first.
- Move low-frequency actions behind overflow (`...`), details, or secondary surfaces.

## 3) Design Tokens (Use Existing Project Tokens)
Use values from:
- `apps/web/src/design-system/tokens/colors.css`
- `apps/web/src/design-system/tokens/spacing.css`
- `apps/web/src/design-system/tokens/typography.css`
- `apps/web/src/design-system/tokens/motion.css`
- `apps/web/src/design-system/tokens/safe-area.css`

### Core palette
- Background: `--bg-primary`, `--bg-secondary`
- Surfaces: `--card-bg`, `--card-bg-strong`
- Borders: `--card-border`
- Text: `--text-primary`, `--text-secondary`, `--text-muted`
- Primary CTA accent: `--accent`, `--accent-soft`

### Spacing rhythm
- Page section spacing: `--space-section`
- Card padding: `--space-card`
- Mobile page x/y: `--space-page-x`, `--space-page-y`

### Motion
- Fast interaction: `--motion-fast`
- Base transition: `--motion-base`
- Easing: `--ease-standard`

### Safe area
- Respect `--safe-top`, `--safe-bottom`, `--safe-left`, `--safe-right` on fixed/sticky elements.

## 4) Layout System
### App shell (`/app/*`)
- Fixed bottom dock with safe-area support.
- Header with lightweight top utility action (`Advanced`).
- Centered content column with readable max width.

### Containers
- Cards use rounded corners and subtle border.
- Never place text/buttons flush to card edges.
- Maintain clear vertical grouping:
  - eyebrow
  - title
  - supporting copy
  - action row

## 5) Interaction Hierarchy
### Button priority
1. Primary CTA
- Accent gradient/button fill.
- One per card/screen when possible.

2. Secondary CTA
- Neutral dark button.
- Used for supporting tasks.

3. Tertiary actions
- Overflow menu (`...`) or subtle text/ghost action.

### Rule
- Avoid rows with 4+ equal-weight actions.
- If >2 actions are needed, keep 2 visible and move the rest into overflow.

## 6) Screen Blueprints (MVP)
## 6.1 Deals
Intent:
- Promote share loop and creation loop.

Must include:
- Chronological feed.
- Top-level create CTA.
- Per-card visible actions:
  - `Share`
  - `Preview`
- Secondary actions in overflow.

Avoid:
- Dense management controls on each card.
- Repetitive button walls.

## 6.2 Redemptions
Intent:
- Fast check-in flow.

Must include:
- Lightweight summary:
  - Today redeemed
  - Pending arrivals
- Primary CTA: `Scan Pass`
- Compact recent activity feed.

Avoid:
- Heavy operational tables on the main screen.

## 6.3 Payouts
Intent:
- Quick financial clarity.

Must include:
- Available balance
- Pending balance
- Withdraw CTA
- Recent payouts list

Avoid:
- Dashboard-density analytics in primary app shell.
- Complex tables by default.

## 6.4 Profile
Intent:
- Identity and shareability.

Must include:
- Avatar
- Name
- Bio
- Share Profile CTA
- Active/current deal snippet
- Recent activity summary

Advanced:
- Keep advanced controls secondary.
- Link to `Advanced Workspace` for legacy tools.

## 7) Forms and Inputs
Rules:
- Prefer single-column on mobile.
- Min touch target height: `44px`.
- Clear label/input association.
- Show validation in plain language.

Media upload:
- Use visual tile with camera icon.
- Auto-upload with immediate local preview.
- Keep URL fields secondary/optional where still needed.

## 8) Typography Rules
- Clear title hierarchy with strong contrast.
- Supporting copy should be short and muted.
- Eyebrows are uppercase, small, and sparse.
- Do not stack large text blocks without spacing.

## 9) Accessibility and UX Quality
- Keyboard focus visible on actionable controls.
- Color contrast must remain readable in dark mode.
- Do not rely on color only for state.
- Loading/empty/error states required for every data panel.

## 10) Performance and Stability
- No layout shift during data load.
- Use skeletons or stable placeholders.
- Keep transitions subtle and fast.
- Avoid blocking interactions during background fetches.

## 11) Legacy/Advanced Boundary
Keep these intact and secondary:
- `/dashboard/*`
- `/admin/*`
- heavy analytics
- bulk operations
- deep payout and booking operations

Primary app should link out via:
- Profile or `Advanced Workspace`

## 12) UI Definition of Done (Per Screen)
A screen is done when:
1. One primary action is obvious.
2. No crowded action rows.
3. Mobile viewport has no overlap/clipping/overflow.
4. Safe-area behavior is correct on iOS.
5. Loading/empty/error states exist.
6. Build passes and route has no dead-end.
7. Legacy bridge is preserved where needed.

## 13) Review Checklist (PR)
- Does this change reduce or increase cognitive load?
- Is action hierarchy clear?
- Are secondary actions hidden behind overflow/details?
- Is this mobile-first at 390px width?
- Does it preserve existing API and legacy routes?
- Does it avoid introducing new nav patterns without explicit approval?

## 14) Future MVP Extension Rules
When adding a new feature:
1. Start with smallest useful card/screen.
2. Keep max 1 primary CTA.
3. Add advanced actions only after core flow feels effortless.
4. Reuse existing tokens; do not add ad hoc colors/spacing first.
5. If a flow gets complex, move power actions to Advanced Workspace.

