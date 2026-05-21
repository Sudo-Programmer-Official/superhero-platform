# Infra Setup Map

## Current Direction
- Firebase Auth: dev/staging/prod project separation
- PostgreSQL: shared RDS instance with dedicated DB/schema isolation
- S3: `openmat-media-prod` in `us-east-1` with project prefix isolation
- API hosting: Render
- Web/Admin hosting: Vercel
- Payments: Stripe Connect Express

## Readiness Matrix
- GitHub: complete
- Monorepo: complete
- Firebase: in progress
- RDS isolation: complete at architecture level
- S3 baseline: complete at architecture level
- Render contracts: ready
- Vercel contracts: ready
- Stripe sandbox checklist: ready
- Observability baseline: complete

## Execution Order
1. Firebase env projects + role claim ops
2. Render and Vercel env value injection
3. RDS migration run + isolation verification
4. S3 bucket policy + prefix policy confirmation
5. Stripe Connect sandbox + webhook wiring
6. Deployment verification checklist execution
