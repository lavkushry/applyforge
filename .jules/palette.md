
## 2024-05-18 - Accessibility: Form Label and Error Bindings
**Learning:** There is a widespread pattern of missing `htmlFor` bindings connecting form labels to inputs, and missing `aria-describedby` linking inputs to validation errors in this codebase (e.g., `apps/web/components/forms/*.tsx`).
**Action:** Always ensure `<label>` elements use `htmlFor` tied to `<Input id="...">`, and ensure validation error messages are linked using `aria-describedby` with `role="alert"`.
