# Deployment Checklist

## 1) Vercel (`apps/web`)
- Framework: `Vite`
- Root Directory: `apps/web`
- Install Command: `pnpm install`
- Build Command: `pnpm build`
- Output Directory: `dist`

Environment variables:
- `VITE_API_URL=https://<render-api-domain>`
- `VITE_FIREBASE_API_KEY=<firebase-web-api-key>`
- `VITE_FIREBASE_PROJECT_ID=<firebase-project-id>`
- `VITE_FIREBASE_AUTH_DOMAIN=<project-id>.firebaseapp.com`
- `VITE_FIREBASE_STORAGE_BUCKET=<project-id>.appspot.com`
- `VITE_FIREBASE_MESSAGING_SENDER_ID=<firebase-sender-id>`
- `VITE_FIREBASE_APP_ID=<firebase-app-id>`

## 2) Render (`apps/api`)
- Root Directory: `apps/api`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Instance Type: `Free` (for infra validation)

Environment variables:
- `DATABASE_URL=<postgresql+asyncpg url>`
- `DATABASE_URL_SYNC=<postgresql url>`
- `DB_SCHEMA=superhero_platform`
- `FIREBASE_PROJECT_ID=<firebase-project-id>`
- `AWS_REGION=us-east-1`
- `S3_BUCKET=openmat-media-prod`
- `LOG_LEVEL=INFO`
- `STRIPE_SECRET_KEY=<stripe secret>`
- `STRIPE_WEBHOOK_SECRET=<stripe webhook secret>`

## 3) Database migration
Run Alembic against the Render DB after deploy:

```bash
cd apps/api
alembic upgrade head
```

## 4) Smoke tests
Health checks:

```bash
curl -sS https://<render-api-domain>/health
curl -sS https://<render-api-domain>/health/db
```

Auth bootstrap checks (replace token):

```bash
TOKEN="<firebase-id-token>"
API="https://<render-api-domain>"
curl -sS -H "Authorization: Bearer $TOKEN" "$API/api/v1/me"
curl -sS -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Test Practitioner"}' "$API/api/v1/me/bootstrap-practitioner"
```

S3 presign check:

```bash
curl -sS -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"folder":"deals","filename":"cover.jpg","content_type":"image/jpeg","content_length":12345}' \
  "$API/api/v1/storage/presign-upload"
```
