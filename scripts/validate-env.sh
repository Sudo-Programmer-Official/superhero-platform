#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-api}"

require_var() {
  local key="$1"
  if [[ -z "${!key:-}" ]]; then
    echo "[env-check] missing: $key" >&2
    return 1
  fi
}

if [[ "$TARGET" == "api" ]]; then
  required=(
    ENV
    DATABASE_URL
    DATABASE_URL_SYNC
    DB_SCHEMA
    CORS_ORIGINS
    FIREBASE_PROJECT_ID
    AWS_REGION
    S3_BUCKET
    S3_PREFIX
    LOG_LEVEL
    LOG_FORMAT
  )

  if [[ "${PAYMENTS_TEST_MODE:-false}" != "true" ]]; then
    required+=(STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET)
  fi
elif [[ "$TARGET" == "web" ]]; then
  required=(
    VITE_API_URL
    VITE_FIREBASE_API_KEY
    VITE_FIREBASE_AUTH_DOMAIN
    VITE_FIREBASE_PROJECT_ID
    VITE_FIREBASE_STORAGE_BUCKET
    VITE_FIREBASE_MESSAGING_SENDER_ID
    VITE_FIREBASE_APP_ID
  )
else
  echo "Usage: $0 [api|web]" >&2
  exit 2
fi

for key in "${required[@]}"; do
  require_var "$key"
done

echo "[env-check] $TARGET env contract looks good"
