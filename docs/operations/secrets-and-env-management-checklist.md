# Secrets and Env Management Checklist

## Checklist
1. Separate env files/secrets for dev, staging, prod.
2. No plaintext secrets committed to repo.
3. Firebase service credentials stored in managed secret store.
4. Stripe keys isolated by env (`test` vs `live`).
5. RDS credentials scoped to project DB/schema access.
6. S3 credentials scoped to project-specific bucket/prefix.
7. Rotate credentials before production launch.
8. Document secret ownership and rotation cadence.
