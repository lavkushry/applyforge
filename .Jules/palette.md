## 2024-04-04 - Missing form label bindings and a11y roles
**Learning:** Found widespread accessibility gap in forms (`auth-form`, `job-create-form`, etc). Inputs lacked `id` attributes linked to `htmlFor` on labels, and validation errors were missing `role="alert"` and `aria-describedby` associations, degrading screen reader experience.
**Action:** Always explicitly map labels to inputs with `id`/`htmlFor`, add `aria-invalid` to inputs with errors, and use `role="alert"` and `aria-describedby` for validation messages.
