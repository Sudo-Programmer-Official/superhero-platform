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
USE_DOCKER_DB="${USE_DOCKER_DB:-0}"

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

if [[ "$USE_DOCKER_DB" == "1" ]]; then
  echo "[dev-stack] Starting local Postgres (docker compose)..."
  (cd "$ROOT_DIR" && docker compose up -d db)
else
  echo "[dev-stack] Using configured external Postgres (Docker DB startup skipped)."
fi

if [[ ! -d "$API_DIR/.venv" ]]; then
  echo "[dev-stack] Creating Python virtual environment..."
  (cd "$API_DIR" && python3 -m venv .venv)
fi

echo "[dev-stack] Installing API dependencies..."
(cd "$API_DIR" && . .venv/bin/activate && pip install -r requirements.txt >/dev/null)

echo "[dev-stack] Ensuring DB schema/tables..."
(cd "$API_DIR" && . .venv/bin/activate && python3 scripts/bootstrap_db.py)

echo "[dev-stack] Aligning Alembic state..."
cd "$API_DIR"
. .venv/bin/activate
set +e
python3 - <<'PY'
from sqlalchemy import create_engine, text
from app.config import settings
engine = create_engine(settings.database_url_sync_resolved)
with engine.connect() as conn:
    has_version = conn.execute(
        text(
            """
            select count(*)
            from information_schema.tables
            where table_schema = :schema and table_name = 'alembic_version'
            """
        ),
        {"schema": settings.db_schema},
    ).scalar()
    app_tables = conn.execute(
        text(
            """
            select count(*)
            from information_schema.tables
            where table_schema = :schema
              and table_name in ('practitioners', 'customers', 'deal_cards', 'wallet_passes')
            """
        ),
        {"schema": settings.db_schema},
    ).scalar()
print("has_version_table=", int(has_version or 0))
print("app_table_count=", int(app_tables or 0))
if has_version:
    raise SystemExit(10)
if app_tables:
    raise SystemExit(20)
raise SystemExit(30)
PY
status="$?"
set -e
SKIP_UPGRADE=0
if [[ "$status" == "10" ]]; then
  echo "[dev-stack] Alembic version table exists."
elif [[ "$status" == "20" ]]; then
  echo "[dev-stack] Existing app tables without alembic_version; stamping head and skipping upgrade."
  python3 -m alembic stamp head
  SKIP_UPGRADE=1
else
  echo "[dev-stack] Fresh schema without alembic_version; running full migration upgrade."
fi
cd "$ROOT_DIR"

if [[ "$SKIP_UPGRADE" != "1" ]]; then
  echo "[dev-stack] Running API migrations..."
  (cd "$API_DIR" && . .venv/bin/activate && python3 -m alembic upgrade head)
else
  echo "[dev-stack] Migration upgrade skipped (already reconciled via stamp)."
fi

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
