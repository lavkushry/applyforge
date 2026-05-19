## 2024-05-15 - Form Accessibility Bindings
**Learning:** Found a widespread pattern across forms (e.g., auth-form.tsx, profile-form.tsx) missing fundamental a11y bindings: labels lacking `htmlFor`/`id` connections to inputs, and validation error messages lacking `aria-describedby` and `role="alert"` associations.
**Action:** Always use `useId()` in React to generate unique, stable IDs for inputs and link them explicitly to their `<label>` and dynamic error messages to ensure screen readers announce context and validation state correctly.
