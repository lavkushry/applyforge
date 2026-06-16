## 2024-05-18 - Form Accessibility Bindings
**Learning:** Next.js form components often lack strict label-input-error bindings. Using React's `useId()` is crucial to establish `htmlFor`/`id` connections for labels, and `aria-describedby`/`aria-invalid` with `role="alert"` for error messages to ensure screen readers correctly interpret form validation state.
**Action:** Always utilize `useId()` to dynamically link `<label>`, `<input>`, and error messages (`role="alert"`) in all new and refactored form components.
