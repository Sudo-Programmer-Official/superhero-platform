# MVP Product Decisions - May 21, 2026

## Product Principle
Optimize for:
- speed
- simplicity
- conversion
- operational reliability

Avoid enterprise flexibility in MVP.

## Core MVP Loop
Practitioner signs up -> creates profile -> creates deal -> shares link -> customer opens -> pays/books -> saves wallet pass -> practitioner redeems.

All feature work must strengthen this loop.

## Locked Decisions

### 1) Deal Lifecycle
States:
- `draft`
- `published`
- `expired`

Rules:
- `draft`: not public, editable, no indexed share links.
- `published`: public URL active, wallet save enabled, checkout enabled, sharing enabled.
- `expired`: public page still visible, visibly expired, checkout disabled, wallet pass inactive.

Out of scope (MVP):
- scheduled publishing
- versioning
- approval/moderation workflows

### 2) Redemption Policy
Default redemption mode: one-time.

Supported modes:
- `single_use`
- `limited_use`
- `unlimited`

Required field:
- `remaining_redemptions`

Operational controls (required):
- manual mark redeemed
- manual restore redemption

### 3) Profile Visibility
Default: public profile.

Field:
- `is_public` boolean

No advanced privacy model in MVP.

### 4) Team Model
MVP model: solo practitioner only.

Constraint:
- tenant == practitioner

No org/team/invite/role matrix in MVP.

### 5) Refund / Cancel Behavior
Refunds:
- manual via Stripe Dashboard only.

Cancellation:
- deal can be marked canceled.
- canceled deal sets wallet status inactive and customer-facing canceled state.

Out of scope:
- in-app refunds
- partial refunds
- cancellation windows
- automated refund/dispute workflows

### 6) Wallet Behavior
Priority:
- Apple Wallet first
- Google Wallet later

Refresh behavior:
- manual refresh on status-changing events:
  - redeemed
  - expired
  - event-time update

No continuous live sync in MVP.

### 7) Booking Strategy
MVP approach:
- external booking URL support only (Calendly/Square/Mindbody/Acuity/etc).

No internal scheduling engine.

### 8) Media Upload Rules
MVP:
- one cover image per deal.

No gallery/media CMS in MVP.

### 9) Auth Strategy
Practitioner:
- Google login
- email/password

Customer:
- avoid forced auth at first purchase when possible.

### 10) Public URL Strategy
Use readable slugs, not UUID public URLs.

Examples:
- `/openmat/marla`
- `/openmat/marla/breathwork-journey`

## North Star UX Metric
Can a practitioner create and share a deal from phone in under 3 minutes?
