# Vertical Slice #1 - Onboarding to Redeem

## Goal
Ship one complete practitioner-to-customer loop:
- practitioner signup/onboarding
- practitioner profile setup
- deal creation + publish
- public profile/deal page
- share link
- Stripe test checkout
- wallet save
- manual redeem

## Scope Boundaries
In scope:
- mobile-first UX path
- one deal cover image
- external booking URL field
- Apple Wallet first path

Out of scope:
- team accounts
- advanced scheduling
- analytics dashboards
- moderation/admin workflow depth

## Acceptance Criteria

### A) Practitioner Onboarding
- can sign in via Google or email/password.
- can complete minimum profile setup.
- profile defaults to `is_public=true`.

### B) Deal Creation
- required fields: title, cover image, price, CTA, date/time.
- lifecycle starts in `draft`.
- publish action moves to `published`.
- cancel action marks canceled and disables checkout.

### C) Public Surface
- public practitioner URL resolves with slug.
- published deal URL resolves with slug.
- expired/canceled state is clearly visible.

### D) Share + Checkout
- share action copies canonical public URL.
- Stripe test checkout runs successfully for published deals.
- checkout blocked for expired/canceled deals.

### E) Wallet + Redeem
- wallet pass can be saved after successful checkout.
- redemption modes support at least `single_use`.
- practitioner can manually mark redeemed and restore.

### F) Reliability
- smoke tests cover critical route + API failures.
- health endpoints operational (`/health`, `/health/db`, `/health/storage`, `/health/firebase`, `/health/stripe`, `/health/schema`).
- CI quality gates pass before merge.

## Execution Order
1. practitioner onboarding path
2. deal creation + publish
3. public profile/deal pages + share action
4. Stripe test checkout hookup
5. wallet save + manual redeem control
6. mobile UX polish + friction pass

## Demo Data Requirement
Seed realistic records:
- 3 practitioners (therapy, yoga, breathwork)
- 6 deals (mix of draft/published/expired)
- 10 fake customers
- redemption examples across supported modes

## Local Validation Commands
```bash
cd apps/api
alembic upgrade head
python3 scripts/seed_demo_data.py
```

Alternative one-command bootstrap:
```bash
pnpm bootstrap:db:seed
```
