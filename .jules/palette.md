## 2024-05-29 - Form Label Bindings
**Learning:** Found widespread missing `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` and `aria-invalid` attributes linking inputs to validation errors equipped with `role='alert'`.
**Action:** Use `useId()` (or explicitly passed IDs) to establish strict bindings. Address these a11y gaps when modifying components.
