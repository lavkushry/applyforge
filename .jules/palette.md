## 2026-05-12 - Fix missing form label bindings and ARIA roles
**Learning:** Forms within `apps/web/components/forms/` often lack `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` and `aria-invalid` attributes linking inputs to validation errors equipped with `role='alert'`.
**Action:** Use `useId()` (or explicitly passed IDs) to establish strict bindings. Address these a11y gaps when modifying components to ensure proper keyboard navigation and screen reader support.
