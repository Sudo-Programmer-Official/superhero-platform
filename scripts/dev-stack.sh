#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"
WEB_DIR="$ROOT_DIR/apps/web"
ADMIN_DIR="$ROOT_DIR/apps/admin"

API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-5173}"
ADMIN_PORT="${ADMIN_PORT:-5174}"
WITH_ADMIN="${WITH_ADMIN:-0}"

API_PID=""
WEB_PID=""
ADMIN_PID=""

cleanup() {
  for pid in "$API_PID" "$WEB_PID" "$ADMIN_PID"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
    fi
  done
}

trap cleanup EXIT INT TERM

echo "[dev-stack] Starting local Postgres (docker compose)..."
(cd "$ROOT_DIR" && docker compose up -d db)

if [[ ! -d "$API_DIR/.venv" ]]; then
  echo "[dev-stack] Creating Python virtual environment..."
  (cd "$API_DIR" && python3 -m venv .venv)
fi

echo "[dev-stack] Installing API dependencies..."
(cd "$API_DIR" && . .venv/bin/activate && pip install -r requirements.txt >/dev/null)

echo "[dev-stack] Running API migrations..."
(cd "$API_DIR" && . .venv/bin/activate && alembic upgrade head)

echo "[dev-stack] Ensuring JS dependencies..."
(cd "$ROOT_DIR" && pnpm install --frozen-lockfile >/dev/null)

echo "[dev-stack] Starting API on :$API_PORT"
(
  cd "$API_DIR"
  . .venv/bin/activate
  uvicorn app.main:app --reload --host 0.0.0.0 --port "$API_PORT"
) &
API_PID="$!"

echo "[dev-stack] Starting web on :$WEB_PORT"
(cd "$WEB_DIR" && pnpm dev --host 0.0.0.0 --port "$WEB_PORT") &
WEB_PID="$!"

if [[ "$WITH_ADMIN" == "1" ]]; then
  echo "[dev-stack] Starting admin on :$ADMIN_PORT"
  (cd "$ADMIN_DIR" && pnpm dev --host 0.0.0.0 --port "$ADMIN_PORT") &
  ADMIN_PID="$!"
fi

echo "[dev-stack] Running. Press Ctrl+C to stop all services."
wait
