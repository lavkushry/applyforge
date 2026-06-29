## 2024-06-29 - Missing explicit form field linking
**Learning:** In this codebase, React Hook Form layouts manually render adjacent `<label>` and `<Input>` components without a central `<FormField>` wrapper. This means accessible linking is not automatic and screen readers cannot associate labels or error messages with their respective inputs.
**Action:** Always explicitly link pairs using `htmlFor` and `id`, and map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` in custom form layouts to ensure screen reader accessibility.
