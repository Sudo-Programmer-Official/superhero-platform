# API Migration Guide

## Run migrations

```bash
cd apps/api
. .venv/bin/activate
alembic upgrade head
```

## Common local failure: `DuplicateTable` / `DuplicateColumn`

This usually means your local schema was changed earlier (manual SQL, branch switch, partial migration run), but Alembic revision history is behind.

Example errors:
- `relation "bookings" already exists`
- `relation "activity_events" already exists`
- `column "..." of relation "..." already exists`

## Team rule for new migrations

Migrations that create tables, columns, indexes, or constraints should be idempotent for local/dev DBs:
- inspect current DB state in migration (`sa.inspect(op.get_bind())`)
- create/add only if missing
- create indexes/constraints only if missing

This keeps `alembic upgrade head` stable across branch switches and partially initialized DBs.

## Recovery options when local DB is out of sync

1. Preferred: keep data, migrate safely

```bash
cd apps/api
. .venv/bin/activate
alembic upgrade head
```

2. If schema already matches code but revision table is behind, stamp current head

```bash
cd apps/api
. .venv/bin/activate
alembic stamp head
```

Use `stamp` only when you are sure your DB schema already matches expected migration state.

3. Full local reset (destructive)
- Drop and recreate local DB/schema.
- Re-run `alembic upgrade head`.

## Helpful checks

Current revision:

```bash
cd apps/api
. .venv/bin/activate
alembic current
```

Migration history:

```bash
cd apps/api
. .venv/bin/activate
alembic history
```

## Notes

- Migration ordering is in `apps/api/alembic/versions`.
- Alembic version table is stored under `settings.db_schema` (configured in `alembic/env.py`).
- For demo flows without Stripe dependency, set `DEMO_CHECKOUT_MODE=true` in `apps/api/.env`.

## Transactional email env contract (SES)

Set these for centralized outbound email:

```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1

MAIL_FROM_EMAIL=hello@openmat.app
MAIL_FROM_NAME=OpenMat
MAIL_REPLY_TO=hello@openmat.app
```

Canonical mail layer:

- Service: `app/services/mail_service.py`
- Templates: `app/templates/emails/*.html` + `*.txt`
- Flow integrations:
  - booking confirmation
  - wallet pass delivery
  - redemption confirmation
  - onboarding welcome

Mail sending is intentionally failure-isolated: booking/redemption operations succeed even if SES fails.

## Local admin role bootstrap (Firebase claims)

OpenMat auth uses Firebase custom claims for role-based access. There is no SQL `users.role` field to update for admin access.

Use the helper script:

```bash
cd apps/api
. .venv/bin/activate
python3 scripts/set_user_role.py --email your-email@example.com --role super_admin
```

You can also target by UID:

```bash
python3 scripts/set_user_role.py --uid <firebase_uid> --role super_admin
```

### Common local mistakes (and fixes)

1. `can't open file ... scripts/scripts/set_user_role.py`
- Cause: running `python3 scripts/set_user_role.py` while already inside `apps/api/scripts`.
- Fix: run from `apps/api`, or use `python3 ./set_user_role.py` if you are inside `apps/api/scripts`.

Correct:

```bash
cd apps/api
python3 scripts/set_user_role.py --email hardimanmatt@icloud.com --role super_admin
```

Or from inside scripts directory:

```bash
cd apps/api/scripts
python3 ./set_user_role.py --email hardimanmatt@icloud.com --role super_admin
```

2. `ModuleNotFoundError: No module named 'firebase_admin'`
- Cause: command not using API virtualenv.
- Fix: activate `apps/api/.venv` (and install deps if needed) before running.

```bash
cd apps/api
. .venv/bin/activate
pip install -r requirements.txt
python3 scripts/set_user_role.py --email hardimanmatt@icloud.com --role super_admin
```

### Safety behavior

- Script is allowed by default only in: `development`, `dev`, `local`, `test`, `staging`.
- For other environments, it exits unless you pass `--force`.

### After role update

1. Sign out from the web app.
2. Sign in again (refreshes token claims).
3. Verify `/me` returns `"role": "super_admin"`.
4. Route guard should redirect to `/admin/overview`.
