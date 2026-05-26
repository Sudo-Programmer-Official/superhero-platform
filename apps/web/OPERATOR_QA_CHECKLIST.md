# Operator Mode Mobile QA Checklist

## Setup
- Enable `VITE_OPERATOR_MODE_ENABLED=true` in `apps/web/.env`.
- Run web app and sign in as practitioner.
- Test on:
  - iPhone Safari (390x844 or real device)
  - Android Chrome (412x915 or real device)

## A. Navigation
1. Operator shell loads after login (not legacy dashboard).
2. Bottom nav shows only `Share` and `Wallet`.
3. `Tools` drawer opens/closes reliably.
4. Tools links navigate correctly to legacy/admin pages.

## B. Share Tab
1. Active offer hero renders without layout overlap.
2. Sticky `Share Active Offer` button remains visible while scrolling.
3. `Copy Link` copies offer URL.
4. `Share` triggers native share sheet (or clipboard fallback).
5. `Preview` opens public offer page.
6. Profile save succeeds for name/avatar/bio fields.
7. Skeleton state appears while offers load.

## C. Create Offer (5-step)
1. Stepper moves forward/back without losing typed values.
2. Live preview updates after each field edit.
3. Minimum required fields gate quick publish correctly.
4. `Quick Publish` creates + publishes successfully.
5. Post-publish sheet appears with actions:
   - Copy Link
   - Share
   - Preview
   - Open Wallet Tab
6. `Done` returns to Share tab.

## D. Wallet Tab
1. Tabs switch between Active / Redeemed / Expired.
2. Pass cards show visual state differences clearly.
3. `Fullscreen QR` opens modal and closes cleanly.
4. `Open Scanner` enters scanner flow in operator mode.
5. Loading skeleton appears before pass list resolves.

## E. Scanner Flow
1. Camera permission prompt appears.
2. Scanning mode hides manual/history cards in operator mode.
3. Scanner frame remains visible and centered.
4. Successful redeem shows attendee/event + clear success state.
5. Duplicate redeem shows already redeemed timestamp messaging.
6. Expired pass shows explicit expired messaging.
7. Invalid code shows explicit invalid messaging.
8. Haptic/feedback feels immediate on mobile.

## F. Keyboard + Safe Area
1. Inputs stay visible when keyboard opens (no clipped fields).
2. Bottom CTAs stay above safe-area inset.
3. No accidental background scroll when sheets/modals open.
4. No horizontal page scrolling.

## G. Performance Feel
1. Route transitions feel instant enough on 4G.
2. No major layout shift while data loads.
3. No blocked interactions during async operations beyond intended disabled states.

## H. Regression Checks
1. Legacy dashboard still works via Tools drawer.
2. Admin routes unaffected.
3. Public booking + success route still function.

## Issue Log Format
- Device:
- Route:
- Steps to reproduce:
- Expected:
- Actual:
- Screenshot/video:
- Severity: blocker / major / minor
