## 2024-06-06 - Proper accessible form inputs
**Learning:** Found that the React Hook Form validation structure in `.tsx` form files does not automatically map the validation error messages (or `errors`) to the respective inputs or properly setup their roles. We need to explicitly bind labels and error messages for better accessibility.
**Action:** Use React's `useId()` and explicit attributes like `htmlFor`, `id`, `aria-invalid`, `aria-describedby`, and `role="alert"` when structuring form fields and their validation errors within Next.js / React components.
