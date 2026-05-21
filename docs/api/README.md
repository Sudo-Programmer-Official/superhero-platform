# API Docs

## Auth and Roles
- Auth: Firebase ID token in `Authorization: Bearer <token>`
- Role claim: `role` custom claim in Firebase token
- Supported roles: `super_admin`, `admin`, `practitioner`, `customer`

## Current Endpoints
- `GET /health`
- `GET /health/db`
- `GET /api/v1/me` (authenticated)
- `POST /api/v1/me/bootstrap-practitioner` (roles: `practitioner`, `admin`, `super_admin`)
- `GET /api/v1/practitioners` (roles: `super_admin`, `admin`)
- `POST /api/v1/practitioners` (authenticated)
- `PATCH /api/v1/practitioners/{practitioner_id}` (roles: `super_admin`, `admin`, `practitioner`)
- `DELETE /api/v1/practitioners/{practitioner_id}` (roles: `super_admin`, `admin`)
- `GET /api/v1/deal-cards` (roles: `super_admin`, `admin`, `practitioner`)
- `POST /api/v1/deal-cards` (authenticated)
- `PATCH /api/v1/deal-cards/{deal_id}` (authenticated; role-aware ownership checks)
- `DELETE /api/v1/deal-cards/{deal_id}` (authenticated; role-aware ownership checks)
- `POST /api/v1/payments/checkout-session` (public checkout initializer)
- `POST /api/v1/payments/webhook` (Stripe payment webhook; signature required)
- `GET /api/v1/wallet-passes` (roles: `super_admin`, `admin`, `practitioner`)
- `POST /api/v1/wallet-passes/issue` (roles: `super_admin`, `admin`, `practitioner`)
- `POST /api/v1/wallet-passes/redeem` (roles: `super_admin`, `admin`, `practitioner`)
- `POST /api/v1/wallet-passes/{wallet_pass_id}/expire` (roles: `super_admin`, `admin`)
- `POST /api/v1/stripe-connect/start` (roles: `practitioner`, `admin`, `super_admin`)
- `GET /api/v1/stripe-connect/status` (roles: `practitioner`, `admin`, `super_admin`)
- `POST /api/v1/stripe-connect/webhook` (Stripe connect webhook; signature required)
- `POST /api/v1/storage/presign-upload` (roles: `super_admin`, `admin`, `practitioner`)
- `POST /api/v1/storage/finalize-asset` (roles: `super_admin`, `admin`, `practitioner`)
- `GET /api/v1/super-admin/tenant-summary` (role: `super_admin`)

## Response/Error Shape
- Errors return:
```json
{
  "error": {
    "code": "internal_error | http_error",
    "message": "...",
    "request_id": "..."
  }
}
```
