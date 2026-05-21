# PWA to Native Transition Plan

## Principle
Ship fast with PWA, but keep architectural seams for native wrappers from day one.

## Required Boundaries
- Domain/business logic separate from platform adapters.
- Route/navigation state separate from web-only primitives.
- Auth/session abstraction compatible with web and native containers.
- Payment/wallet adapters that can branch by runtime.

## Runtime Adapter Targets
- Push notifications
- Deep links/universal links
- Wallet integration APIs
- Device permissions and secure storage

## Build Rules
- Do not hardcode web-only storage or browser-global assumptions in domain modules.
- Keep API contracts stable so native clients can reuse backend unchanged.
- Maintain a shared design language between PWA and native shells.
