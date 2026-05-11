## 2024-05-24 - Form Accessibility Bindings
**Learning:** Found that basic form components (like `AuthForm`) lacked explicit `htmlFor`/`id` connections between labels and inputs, as well as proper `aria-invalid` and `aria-describedby` associations for error messages equipped with `role="alert"`. This pattern was widespread and hindered screen reader compatibility.
**Action:** Always implement `useId()` (or explicitly passed IDs) to establish strict `htmlFor` bindings and use `aria-describedby` alongside `role="alert"` for form validation errors across all newly authored or modified forms.
