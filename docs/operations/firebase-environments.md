# Firebase Environments Setup

## Environment Topology
- `superhero-dev`
- `superhero-staging`
- `superhero-prod`

## Required Config Per Project
- Auth providers enabled (Email/Password, Google if needed)
- Custom claims enabled for roles:
  - `super_admin`, `admin`, `practitioner`, `customer`
- Authorized domains:
  - web app domains per env
  - preview URLs as needed

## Service Account and Admin SDK
- Use separate service accounts per environment.
- Store credentials in environment-specific secret stores only.
- Do not share prod service account keys with dev/staging.

## Role Claim Governance
- Claims set by admin-only backend operation.
- Role changes logged with request ID and actor metadata.
