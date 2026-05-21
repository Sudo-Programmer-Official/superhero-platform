# Mobile Interaction Patterns

## Navigation
- Bottom nav for primary destinations.
- Contextual top actions for share/save/edit.
- Back behavior must map cleanly to native stacks later.

## Gesture + Touch
- Minimum 44px touch targets.
- Swipe-friendly card sections where meaningful.
- Avoid hidden gestures for critical actions.

## Feedback
- Inline status feedback for saves, payment, wallet add, redemption.
- Loading skeletons over spinner-only states.
- Request ID surfaced in error states for support and debugging.

## PWA -> Native Compatibility
- Keep route/state model wrapper-safe.
- Isolate device APIs behind adapters.
- Treat push/deep-link as pluggable capabilities, not core route assumptions.
