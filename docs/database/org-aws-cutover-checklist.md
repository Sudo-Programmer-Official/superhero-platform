# Org AWS Cutover Checklist

## Goal
Migrate `superhero-platform` database/runtime from current shared setup to organization AWS account with minimal risk and minimal downtime.

## Design Principles
- Keep app contract stable: same table names, same schema name, same migration flow.
- Change infrastructure bindings, not application logic.
- Keep rollback path ready before cutover starts.

## Pre-Cutover Requirements
- Org AWS account created and access approved.
- Target RDS Postgres provisioned in org account.
- `superhero_platform` database created on target RDS.
- `superhero_platform` schema created or migration user authorized to create it.
- Security groups/VPC routing allow API runtime to connect to target RDS.
- Secrets manager/parameter store entries prepared for target DB credentials.

## Naming/Parity Rules
- Keep `DB_SCHEMA=superhero_platform`.
- Keep migration history chain unchanged.
- Keep app env key names unchanged:
  - `DATABASE_URL`
  - `DATABASE_URL_SYNC`
  - `DB_SCHEMA`

## Data Migration Strategy (Recommended)
1. Freeze risky schema changes during migration window.
2. Take source snapshot/backup.
3. Restore/import to target org RDS.
4. Run `alembic current` on source and target; confirm parity.
5. Run `alembic upgrade head` on target (should be no-op or final delta only).
6. Validate row counts for critical tables.

## Cutover Steps
1. Put API in maintenance/drain mode if needed.
2. Update runtime secrets to target org RDS URLs.
3. Restart API services.
4. Run health checks:
   - `/health`
   - `/health/db`
5. Verify app writes and reads for:
   - practitioners
   - deal cards
   - wallet passes
   - customers

## Verification Queries
- Confirm schema isolation:
```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'superhero_platform'
ORDER BY table_name;
```

- Confirm no accidental app tables in `public`:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('practitioners', 'deal_cards', 'wallet_passes', 'customers');
```

## Rollback Plan
- Keep source DB untouched during first cutover.
- If validation fails:
  1. Re-point secrets back to source DB.
  2. Restart API services.
  3. Confirm `/health/db` and smoke flows.
- Document failure cause before second cutover attempt.

## Post-Cutover Hardening
- Rotate DB credentials.
- Enforce least-privilege DB user grants.
- Enable automated backups and retention policy.
- Configure DB monitoring/alerts in org account.
- Record final topology in architecture docs.
