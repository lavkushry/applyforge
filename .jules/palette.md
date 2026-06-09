## 2024-06-09 - Strict Form Field Bindings
**Learning:** Forms in this codebase often lack `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby`/`aria-invalid` attributes linking inputs to validation errors equipped with `role='alert'`.
**Action:** Always use React's `useId()` to establish strict label bindings, and explicitly connect error text to inputs using `aria-describedby` and `role="alert"` for proper screen reader announcement of validation states.
