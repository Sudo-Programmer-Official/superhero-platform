# Coding Source of Truth

This file is the engineering contract for `superhero-platform`.

## Locked Stack
- Frontend: Vue 3 + TailwindCSS
- UI library usage: Element Plus for admin/forms/internal tooling only
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Architecture: modular monolith
- App mode: PWA-first

## Target Repo Shape
```text
apps/
  web/
  api/
  admin/

packages/
  ui/
  shared/
  wallet/
  auth/

docs/
  product/
  architecture/
  api/
  wallet-system/
  roadmap/
  flows/
  payments/
```

## Non-Negotiable Rules
- Optimize for real-world engagement loops, not attention metrics.
- Do not overengineer or split into microservices in MVP.
- Keep modules clear and separable for future extraction.
- Keep customer-facing surfaces mostly custom Tailwind UI.
- Keep files small and readable; avoid giant components/services.

## MVP Exclusions
Do not build in MVP:
- marketplace discovery
- messaging systems
- AI recommendations
- advanced memberships
- community feeds
- reviews
- notification-heavy systems

## Delivery Priority
1. Authentication
2. Practitioner profile system
3. Deal card engine
4. Stripe payment flow
5. Wallet pass generation
6. QR redemption
