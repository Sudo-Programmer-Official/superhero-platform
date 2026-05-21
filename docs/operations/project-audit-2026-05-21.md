# Project Audit - May 21, 2026

## Scope
- Monorepo audit across `apps/api`, `apps/web`, `apps/admin`, shared docs, and local run/deploy scripts.
- Focus: runtime readiness, deployment correctness, security/config hygiene, and delivery gaps vs MVP goals.

## Current State Summary
- Backend/API structure is solid for MVP foundation (modular routes, services, repositories, Alembic migrations).
- Web app builds successfully and has auth/session + API integration wiring.
- Core deployment flow is defined for Render (API) and Vercel (web).
- Local one-command startup exists via `scripts/dev-stack.sh`.
- Significant gaps remain in automated testing, CI quality gates, and feature completion (admin, wallet/redeem flows, analytics depth).

## What Was Verified
- API route composition and service layering:
  - `apps/api/app/api/v1/router.py`
  - `apps/api/app/services/*`
- API startup and config compile checks:
  - `python3 -m py_compile` passed for key API modules.
- Web production build:
  - `pnpm build:web` passed.
- Deployment references:
  - `docs/deploy/deployment-checklist.md`
  - `infra/render.yaml`

## Strengths
- Clear backend boundaries (routes -> services -> repositories -> models).
- DB migration history is present and versioned (`apps/api/alembic/versions/*`).
- Auth guard model exists with role checks (`apps/api/app/auth/dependencies.py`).
- Observability scaffolding exists (request context + structured logging modules).
- Frontend has route guards and session watcher flow (`apps/web/src/router/index.ts`, `apps/web/src/stores/session.ts`).

## Risks / Gaps Identified
- No automated tests detected (backend/frontend/integration/e2e).
- No lint/type/test quality gates at root scripts level.
- Admin app is scaffold-level only (`apps/admin/src/App.vue`).
- Root `.env.example` contains outdated key `VITE_API_BASE` while app uses `VITE_API_URL`.
- Deployment health depends on manual env correctness; no preflight validation script exists.
- API startup previously had fragile URL parsing behavior (now improved in code), but no regression tests cover this.
- PWA/service-worker behavior needed hardening to avoid stale asset blank-screen failures (now patched), but still untested in CI.

## Pending Work (Prioritized)

### P0 - Must Do Before Broader Production Use
- Add automated backend tests for:
  - auth dependency behavior (`401/403` cases),
  - `/payments/checkout-session` and webhook flows,
  - `/health` and `/health/db`.
- Add frontend smoke tests for:
  - auth route guard,
  - API failure handling,
  - service-worker update behavior after deploy.
- Add CI pipeline checks:
  - backend test command,
  - frontend build,
  - lint/type checks.
- Fix env contract drift:
  - replace `VITE_API_BASE` with `VITE_API_URL` in root `.env.example`.

### P1 - Should Do Next
- Add deployment preflight script validating required env vars for Render/Vercel.
- Add API integration test harness against local Postgres + Alembic migrations.
- Add explicit CORS domain rollout playbook for Vercel preview vs production domains.
- Expand error handling/telemetry around payment + storage paths for incident triage.

### P2 - Product/Platform Completion
- Build real admin workflows (current app is placeholder).
- Complete wallet/redeem operational loop and add reconciliation/reporting.
- Add analytics instrumentation and dashboard-level KPIs for MVP success criteria.
- Add backup/rollback runbooks for schema and deployment incidents.

## Recommended Next 7-Day Execution Plan
1. Day 1-2: test scaffolding (pytest + minimal frontend test runner) + CI setup.
2. Day 3: P0 API tests for auth/payments/health.
3. Day 4: frontend route/API smoke tests + service-worker regression test.
4. Day 5: env contract cleanup + deploy preflight script.
5. Day 6-7: admin scope definition and first functional admin slice.

## Audit Verdict
- Foundation quality: **Good**
- Production resilience: **Moderate risk until P0 items are completed**
- MVP completeness: **Partial (core scaffolding done, several critical deliverables pending)**
