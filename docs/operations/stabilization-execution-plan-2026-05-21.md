# Stabilization Execution Plan - May 21, 2026

## Objective
Stabilize production reliability before expanding feature scope.  
Platform focus: identity + conversion + wallet distribution.

## Priority Order (Execution)
1. CI/CD quality gates
2. Runtime/env validation
3. Backend automated tests
4. Frontend smoke tests
5. Deployment hardening

## Completed In This Pass
- Added CI workflow: `.github/workflows/quality-gates.yml`
  - API pytest job
  - Web build job
- Added startup/runtime validation:
  - required env checks
  - DB connectivity check
  - schema existence check
  - Firebase initialization check
  - S3 accessibility check
  - Stripe health check
- Added health endpoints:
  - `/health/storage`
  - `/health/firebase`
  - `/health/stripe`
  - `/health/schema`
- Added env validation script:
  - `scripts/validate-env.sh` (`api` and `web` modes)
- Added backend test baseline:
  - `apps/api/tests/*`
  - `apps/api/pytest.ini`

## Frontend Architecture Direction
Move from generic page/component sprawl to feature modules:
- `src/modules/auth`
- `src/modules/practitioner`
- `src/modules/deal-cards`
- `src/modules/wallet`
- `src/modules/bookings`
- `src/modules/memberships`
- `src/modules/admin`

## UX/Architecture Guardrails
- Mobile-first interactions as default.
- Minimize onboarding steps to first value.
- Optimize share flows from deal creation to conversion.
- Keep wallet save/redeem loops first-class in nav and actions.
- Preserve production-safe PWA updates and cache invalidation behavior.
- Avoid deep admin/dashboard complexity until identity/conversion/wallet loops are stable.

## Next Implementation Sequence
1. CI + test foundation expansion
2. Env/deploy validation hardening
3. Stripe Connect skeleton completion
4. S3 upload pipeline hardening
5. Wallet/redeem operational loop completion
6. PWA update-flow resilience + regression tests
