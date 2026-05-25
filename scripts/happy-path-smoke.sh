#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

API_BASE="${API_BASE:-http://127.0.0.1:8000}"
WEB_BASE="${WEB_BASE:-http://127.0.0.1:5173}"

echo "[smoke] OpenMat Happy Path smoke starting"
echo "[smoke] API_BASE=$API_BASE"
echo "[smoke] WEB_BASE=$WEB_BASE"

if [[ ! -f "$ROOT_DIR/apps/api/.env" ]]; then
  echo "[smoke] missing apps/api/.env" >&2
  exit 1
fi

if ! grep -q '^DEMO_CHECKOUT_MODE=true' "$ROOT_DIR/apps/api/.env"; then
  echo "[smoke] warning: DEMO_CHECKOUT_MODE=true not set in apps/api/.env"
  echo "[smoke] this flow is intended for demo-mode checkout"
fi

echo "[smoke] checking API health..."
curl -fsS "$API_BASE/health" >/dev/null
echo "[smoke] API health ok"

echo "[smoke] checking web root..."
curl -fsS "$WEB_BASE" >/dev/null
echo "[smoke] web root ok"

echo
echo "[smoke] Manual verification checklist (run in app):"
echo "  1) Practitioner: create + publish deal."
echo "  2) Open public link and complete booking."
echo "  3) Verify booking appears in /dashboard/bookings."
echo "  4) Verify wallet pass appears in /dashboard/wallet-passes."
echo "  5) Redeem QR in /dashboard/redemptions."
echo "  6) Verify dashboard metrics + admin overview update."
echo
echo "[smoke] Detailed checklist:"
echo "  docs/OPENMAT_HAPPY_PATH_QA.md"

