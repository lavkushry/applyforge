## 2024-05-02 - Form Label and Error Accessibility
**Learning:** Widespread missing form label bindings (`htmlFor`/`id`) connecting labels to inputs, and missing `aria-describedby` linking inputs to validation errors equipped with `role='alert'` across `apps/web/components/forms/`.
**Action:** When creating or modifying form components, ensure all inputs have an `id` that is referenced by their `label` via `htmlFor`. Add `aria-invalid` to inputs with errors, and link error messages (which should have `role='alert'`) using `aria-describedby`.
