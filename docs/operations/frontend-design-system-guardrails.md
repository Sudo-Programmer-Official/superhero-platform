# Frontend Design-System Guardrails

## Purpose
Keep product UI evolution fast, safe, and consistent while preserving a premium mobile-first experience.

## Rules
1. Product UI must use design-system tokens and primitives first.
2. Element Plus is for `apps/admin` and internal tooling, not primary product surfaces.
3. Avoid large one-off utility stacks in feature components.
4. Prefer composition:
   - `primitives` for stable atoms
   - `patterns` for reusable business UI blocks
5. Every new interactive component must work for phone first, then scale to tablet/desktop.

## Token Usage
- Use CSS variable tokens from `src/design-system/tokens/*`.
- Do not hardcode colors/spacing in feature modules unless justified.
- Dark theme is canonical for MVP.

## PR Checklist
- Spacing rhythm is consistent.
- Typography hierarchy is clear.
- Primary CTA is visually obvious.
- Tap targets are mobile-friendly.
- Loading/error states are present for key actions.
- No fake device-frame UI patterns.
