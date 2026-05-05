## 2025-02-20 - Missing Form Label Bindings
**Learning:** Widespread lack of `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` linking inputs to validation errors equipped with `role='alert'` across `apps/web/components/forms/`.
**Action:** When adding or modifying forms, always ensure proper label-to-input association and screen-reader-friendly validation errors using ARIA attributes.
