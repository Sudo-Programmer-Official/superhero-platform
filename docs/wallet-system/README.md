# Wallet System Docs

## Lifecycle States
- `issued`
- `redeemed`
- `expired`

## Lifecycle Rules
- `issued -> redeemed`
- `issued -> expired`
- `redeemed` is terminal for MVP
- `expired` is terminal for MVP

## API Contracts
- Issue: `POST /api/v1/wallet-passes/issue`
- Redeem by QR: `POST /api/v1/wallet-passes/redeem`
- Expire: `POST /api/v1/wallet-passes/{wallet_pass_id}/expire`

## Notes
- QR code is generated server-side on issue.
- State transitions are enforced in service layer.
