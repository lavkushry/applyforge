## 2024-06-08 - Missing Form Accessibility Bindings
**Learning:** React Hook Form usage in this codebase often lacks explicit `htmlFor`/`id` bindings and `aria-describedby` links for validation errors, severely impacting screen reader experience.
**Action:** Always use `useId()` in form components to establish strict ID bindings between labels, inputs, and role="alert" error messages.
