# Stripe Connect Direction

Model: Connect Express.
- Practitioner owns connected account
- Customer pays practitioner directly
- Platform fee toggled on later via application fees

Future support:
- subscriptions
- transaction fees
- revenue split controls

## Current API Contracts
Connect onboarding:
- `POST /api/v1/stripe-connect/start`
- `GET /api/v1/stripe-connect/status`
- `POST /api/v1/stripe-connect/webhook`

Checkout and payment:
- `POST /api/v1/payments/checkout-session`
- `POST /api/v1/payments/webhook`

## MVP Notes
- Uses real Stripe SDK `Account.create` + `AccountLink.create` for Connect Express onboarding links.
- Webhook signature verification is enforced using `STRIPE_WEBHOOK_SECRET`.
- `account.updated` and `account.application.deauthorized` events sync onboarding state to practitioner records.
- `checkout.session.completed` webhook decrements deal capacity and issues wallet pass idempotently.


Test mode:
- Set `PAYMENTS_TEST_MODE=true` to simulate paid checkout happy flow without Stripe redirect/webhook.
- In test mode, checkout session API decrements slots and issues wallet pass immediately.
