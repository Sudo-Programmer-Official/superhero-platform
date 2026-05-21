# Super Admin and Tenant Architecture

## Roles
- `super_admin`: cross-tenant control and analytics
- `admin`: tenant-level operational management
- `practitioner`: own profile/deals/events
- `customer`: purchase, wallet, redemption

## Initial Controls
- Tenant summary dashboard
- Practitioner lifecycle management
- Event capacity and redemption oversight
- Operational analytics snapshots

## Security
- Firebase token verification required for protected APIs.
- Role checks at route boundary and service-level invariants.
- Every admin mutation must be auditable via structured logs and request IDs.
