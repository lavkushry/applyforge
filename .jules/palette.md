## 2024-05-17 - Missing form label bindings and ARIA roles
**Learning:** Forms within `apps/web/components/forms/` often lack `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` and `aria-invalid` attributes linking inputs to validation errors equipped with `role='alert'`.
**Action:** Use `useId()` (or explicitly passed IDs) to establish strict bindings. Address these a11y gaps when modifying components.
