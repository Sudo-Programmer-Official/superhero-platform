from __future__ import annotations

import os
import sys
from argparse import ArgumentParser

from sqlalchemy import create_engine, text

# Allow running as: python3 scripts/bootstrap_db.py from apps/api
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import settings
from app.models import Base


def ensure_schema_and_tables() -> None:
    engine = create_engine(settings.database_url_sync_resolved)
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.db_schema}"'))
        conn.execute(text(f'SET search_path TO "{settings.db_schema}"'))
        Base.metadata.create_all(bind=conn)


def main() -> None:
    parser = ArgumentParser(description="Bootstrap DB schema/tables and optionally seed demo data.")
    parser.add_argument("--seed", action="store_true", help="Also run demo seed data.")
    args = parser.parse_args()

    ensure_schema_and_tables()
    print("DB schema/tables ensured.")

    if args.seed:
        from seed_demo_data import main as seed_main  # local script import
        import asyncio

        asyncio.run(seed_main())


if __name__ == "__main__":
    main()
