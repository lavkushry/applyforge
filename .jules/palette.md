## 2024-05-22 - Form Accessibility Bindings

**Learning:** This codebase frequently omits standard form accessibility bindings, such as `htmlFor` on labels, `id` on inputs, `aria-invalid` for error states, and `aria-describedby` referencing error messages. Screen readers require these explicit connections to understand form fields.

**Action:** Whenever reviewing or updating forms, use `useId()` from React to generate unique base IDs for a component. Apply these IDs to explicitly bind labels (`htmlFor`) to inputs (`id`). Additionally, use `aria-invalid` and `aria-describedby` on the input, and ensure the corresponding error message element has the matching `id` and `role="alert"`.