## 2024-06-25 - Missing strict form label bindings
**Learning:** React hook forms across the codebase frequently omit explicit IDs and ARIA properties, which breaks screen reader capability for linking input fields to their labels and respective inline error messages.
**Action:** Use `useId()` consistently to establish robust a11y bindings (`htmlFor`, `id`, `aria-describedby`, `aria-invalid`, `role="alert"`) when building or modifying inputs with dynamic inline validation feedback.
