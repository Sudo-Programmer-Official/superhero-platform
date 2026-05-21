# Database Isolation Policy

## Purpose
Define non-negotiable isolation rules for running `superhero-platform` on a shared AWS RDS PostgreSQL instance used by other projects.

## Isolation Contract
- Shared infrastructure: same RDS instance is allowed.
- Shared application tables: not allowed.
- This project must use:
  - dedicated database name
  - dedicated schema
  - dedicated DB role/user credentials where possible

## Naming Convention
- Database name: `superhero_platform`
- Schema name: `superhero_platform`
- Alembic version table: `superhero_platform.alembic_version`
- Runtime search path: `superhero_platform`

If environment constraints require a different DB name, keep schema isolation unchanged and update only env/config values.

## Environment Variables
Required:
- `DATABASE_URL` (async URL for app runtime)
- `DATABASE_URL_SYNC` (sync URL for Alembic)
- `DB_SCHEMA` (must be project-specific)

Example:
```env
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<rds-host>:5432/superhero_platform
DATABASE_URL_SYNC=postgresql://<user>:<pass>@<rds-host>:5432/superhero_platform
DB_SCHEMA=superhero_platform
```

## Access Control Rules
- Use a project-specific DB user when possible.
- Minimum privileges:
  - connect to project DB
  - usage/create on project schema
  - DML/DDL only for project schema objects
- Do not grant broad privileges on other schemas.
- Do not use superuser credentials in application runtime.

## Migration Rules
- Every migration must target only `DB_SCHEMA`.
- Migration scripts must not create/alter tables in `public` or other project schemas.
- Foreign keys must reference tables in the same schema unless explicitly approved.
- Downgrades must only drop objects in this project schema.

## Operational Guardrails
- No cross-project joins in application code.
- No shared tables between PlanCraft AI, SalonFlow, Agentic SDLC, and Superhero Platform.
- No copy-paste migrations between projects without schema review.
- Schema changes require migration PR review before deploy.

## Deployment Runbook
1. Confirm env vars point to correct DB + schema.
2. Run migration:
   - `cd apps/api`
   - `alembic upgrade head`
3. Verify objects are isolated:
   - `SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'superhero_platform';`
4. Verify no new app tables appeared in `public`.

## Incident Response
If a table is accidentally created outside this schema:
1. Freeze deploys.
2. Capture object list and migration revision.
3. Create corrective migration to move/drop incorrect objects.
4. Re-run verification query and document fix in release notes.

## Org AWS Migration Readiness
- Keep project DB and schema names stable across environments.
- Keep env variable names stable so deploy pipelines only swap secret values.
- Keep Alembic history linear and consistent before cutover.
- Maintain tested rollback by preserving source DB and old secrets until post-cutover validation is complete.
- Follow `docs/database/org-aws-cutover-checklist.md` for execution.
