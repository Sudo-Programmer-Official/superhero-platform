# RDS Schema Isolation Checklist

## Required
- DB name dedicated to project (`superhero_platform` preferred).
- Schema dedicated to project (`superhero_platform`).
- App runtime search path set to project schema.
- Alembic version table under project schema.

## Verification SQL
```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'superhero_platform'
ORDER BY table_name;
```

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
AND table_name IN ('practitioners','deal_cards','wallet_passes','customers');
```
