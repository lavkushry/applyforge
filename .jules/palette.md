## 2024-05-24 - Widespread missing form label bindings
**Learning:** Forms across the application (e.g., auth-form, job-create-form, profile-form) often lack basic accessibility bindings like `htmlFor`/`id` connecting labels to inputs, and lack `aria-describedby` attributes linking inputs to their validation errors equipped with `role='alert'`.
**Action:** When creating or modifying forms, always ensure explicit label-input associations using `htmlFor` and `id`, and properly link error messages to their respective inputs using `aria-describedby` and `aria-invalid` attributes.
