# Platform Implementation Roadmap

## Phase A: Core Foundations (Current)
- Firebase auth middleware and role guards.
- Postgres schema + Alembic.
- Structured observability and request tracing.
- Service/repository CRUD architecture baseline.

## Phase B: Practitioner + Deal Core
- Practitioner onboarding/profile APIs.
- Deal card CRUD and scheduling rules.
- Share-link and QR generation interfaces.

## Phase C: Commerce + Wallet
- Stripe Connect Express onboarding and checkout sessions.
- Wallet pass issuance lifecycle (issued, redeemed, expired).
- Redemption endpoint + attendance tracking.

## Phase D: Super Admin + Tenant Controls
- Tenant/practitioner management workflows.
- Organization-level controls and policy surfaces.
- Analytics dashboard baseline: views, conversions, redemptions.

## Phase E: Native-Ready Evolution
- PWA shell hardened for wrapper compatibility.
- Deep-link and push abstraction layer.
- Native wallet and device API integration plan.
