# Vercel + Render Environment Contracts

## Web/Admin (Vercel)
Required env vars:
- `VITE_API_BASE`
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_PAYMENTS_TEST_MODE`

## API (Render)
Required env vars:
- `ENV`
- `DATABASE_URL`
- `DATABASE_URL_SYNC`
- `DB_SCHEMA`
- `CORS_ORIGINS`
- `FIREBASE_PROJECT_ID`
- `LOG_LEVEL`
- `LOG_FORMAT`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_CONNECT_CLIENT_ID`
- `STRIPE_COUNTRY`
- `PAYMENTS_TEST_MODE`

## Rule
- Keep var names stable across environments.
- Only values differ across dev/staging/prod.
