# In-Person Superhero Platform

Mobile-first platform for real-world practitioners to create offers/events, accept payments, issue wallet passes, and drive repeat attendance through social sharing.

## Monorepo Structure
- `apps/web` - customer + practitioner mobile-first Vue app
- `apps/admin` - internal admin operations panel (Element Plus heavy)
- `apps/api` - FastAPI modular monolith backend
- `packages/ui` - shared design primitives
- `packages/shared` - shared types/utilities
- `packages/wallet` - wallet pass domain logic/contracts
- `packages/auth` - auth helpers/contracts
- `docs/*` - product, architecture, flows, API, roadmap, payments

## Quick Start
1. Copy `.env.example` to `.env`
2. Configure DB env vars in `apps/api/.env` (AWS RDS is default).
3. Start API:
   - `cd apps/api && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
   - `alembic upgrade head`
   - `uvicorn app.main:app --reload --port 8000`
4. Start apps:
   - `pnpm install`
   - `pnpm dev:web`
   - `pnpm dev:admin`

Optional local Postgres fallback:
- `USE_DOCKER_DB=1 pnpm dev:stack`

## Auth + Data Direction
- Auth/session layer: Firebase Auth
- Primary database: PostgreSQL on existing shared AWS RDS instance
- API/business logic: FastAPI
- Isolation model: dedicated DB name and dedicated schema for this project; no shared application tables

## MVP Priority
1. Authentication
2. Practitioner profile system
3. Deal card engine
4. Stripe checkout/connect flow
5. Wallet pass generation
6. QR redemption
