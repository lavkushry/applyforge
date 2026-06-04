## 2024-06-04 - Missing form bindings in standard components
**Learning:** React Hook Form components in this codebase often omit `htmlFor`/`id` bindings and `aria-describedby` links between inputs and validation errors, causing screen reader users to lack context on form fields and error states.
**Action:** Always verify `useId` is imported and used to bind labels, inputs, and `role="alert"` error messages together in form components.
