# OpenMat Happy Path QA (June 14)

Use this checklist before demo/use sessions. Goal: validate the full loop end-to-end.

## Environment

1. API running with `DEMO_CHECKOUT_MODE=true` in `apps/api/.env`.
2. Web app running on local/staging URL.
3. At least one practitioner account with dashboard access.
4. At least one operator/admin account with redemption + admin access.

## Practitioner Flow

1. Sign in as practitioner.
2. Create a new deal with:
   - title
   - location
   - start/end time
   - capacity
   - wallet enabled
3. Publish the deal.
4. Confirm share/public link opens.

Expected:
- Deal appears on practitioner Deals page.
- Deal status is `Published`.
- Activity feed includes a publish event.

## Customer Booking Flow

1. Open public deal link in a separate browser/session.
2. Enter customer name/email.
3. Complete checkout.

Expected:
- Redirect shows booking success state.
- Booking is created in backend (`bookings`).
- Wallet pass is generated (`wallet_passes`).

## Wallet Pass Flow

1. Open wallet pass center as practitioner/operator.
2. Verify new pass appears with:
   - QR code
   - active status
   - attendee/deal details

Expected:
- Pass can be opened and QR is visible.
- Activity feed includes `wallet.generated`.

## Redemption Scanner Flow

1. Open Redemption Scanner.
2. Scan pass QR (or manual redeem code fallback).

Expected:
- Success state with redeemed timestamp and operator label.
- Pass status changes to redeemed.
- Activity includes `wallet.redeemed` and `redemption.success`.

## Negative Redemption States

1. Scan same pass again.
   - Expect `Already redeemed` with previous timestamp.
2. Scan invalid code.
   - Expect `Invalid pass`.

## Dashboard + Admin Sync

1. Practitioner dashboard updates:
   - Total bookings
   - Revenue
   - Redemptions
   - Conversion rate
2. Admin overview reflects same underlying operational changes.

Expected:
- No hardcoded metric values.
- Live values update after booking/redemption.

## Auth Trust Checks

1. On sign-in screen, use `Forgot password?`.
2. Confirm reset email flow succeeds with proper message.

## Final Sign-off

1. No raw 500s in browser/API logs during flow.
2. No dead buttons in the main loop.
3. Mobile scanner permission + fallback works.
4. Operator can complete one full redeem cycle in < 30 seconds.

