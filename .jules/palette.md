## 2026-04-18 - Missing label bindings and error associations in forms
**Learning:** Widespread accessibility issues exist across forms in `apps/web/components/forms/`, specifically lacking `htmlFor`/`id` bindings to connect labels to inputs, and missing `aria-describedby` linking inputs to validation errors with `role='alert'`.
**Action:** Always map form labels to inputs using `htmlFor` and `id`, and add `role='alert'` alongside `aria-describedby` to validation errors.
