## 2024-06-03 - Missing form label bindings

**Learning:** Discovered a pattern in `apps/web/components/forms/` where `htmlFor`/`id` bindings connecting labels to inputs were frequently missing, as well as missing `aria-describedby` and `aria-invalid` attributes linking inputs to validation errors equipped with `role='alert'`.

**Action:** Whenever modifying form components in this app, utilize `useId()` (or explicitly passed IDs) to establish strict semantic bindings between labels and inputs, and ensure validation errors are linked to the input via `aria-describedby` for improved accessibility and screen reader support.
