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
- Start onboarding: `POST /api/v1/stripe-connect/start`
- Status: `GET /api/v1/stripe-connect/status`

## MVP Notes
- Current implementation provides stable backend contracts and persisted account metadata.
- Replace placeholder onboarding URL generation with real Stripe Account Link API in next integration step.
