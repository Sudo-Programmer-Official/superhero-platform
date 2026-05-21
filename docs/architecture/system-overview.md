# System Overview

Architecture: modular monolith with Vue (web/admin), FastAPI (api), and Postgres.

Core modules:
- Identity
- Deal Engine
- Wallet System
- Payments
- Analytics
- Share Layer

Initial deployment:
- web/admin on Vercel
- api on Render
- Postgres on existing shared AWS RDS instance

Identity architecture:
- Firebase Auth for authentication/session verification
- PostgreSQL as system of record for app domain entities

Data isolation rule:
- This project uses its own DB name and schema on RDS.
- Application tables must remain isolated from other projects (PlanCraft AI, SalonFlow, Agentic SDLC).
