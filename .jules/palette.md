## 2024-10-24 - Explicit Form Label Bindings
**Learning:** Forms in this application often lack strict `htmlFor` to `id` bindings and miss crucial ARIA attributes (`aria-describedby`, `aria-invalid`) for error messages, causing screen readers to lose context during validation.
**Action:** Always use `useId()` (or passed IDs) to explicitly connect labels to inputs, and link inputs to their respective error messages (equipped with `role="alert"`) to ensure robust keyboard and screen reader accessibility.
