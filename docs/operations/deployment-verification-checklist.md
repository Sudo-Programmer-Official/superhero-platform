# Deployment Verification Checklist

## Pre-Deploy
1. `alembic upgrade head` completed on target env.
2. Firebase env points to matching frontend/backend env.
3. Stripe env keys and webhook secrets validated.
4. CORS origins aligned with deployment domains.

## Post-Deploy API
1. `GET /health` returns `ok`.
2. `GET /health/db` returns `ok`.
3. Auth-protected endpoint validates token + role checks.
4. Structured logs include `request_id`.

## Post-Deploy Product Smoke
1. `/me` works for authenticated user.
2. bootstrap practitioner profile works once.
3. DealCard create/list/update/delete works for allowed roles.
4. Super-admin tenant summary endpoint works.

## Rollback Trigger
- Any auth regression, migration inconsistency, or failed core flow blocks rollout.
