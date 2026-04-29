## 2024-04-29 - Missing Form Label Bindings
**Learning:** Found a widespread pattern of forms lacking `htmlFor` and `id` bindings connecting labels to inputs (e.g., in `role-create-form.tsx`). This breaks screen reader accessibility and clickable label behavior.
**Action:** When creating or modifying forms, always ensure `<label htmlFor="id">` is explicitly bound to `<input id="id" />`. Additionally, ensure validation errors use `role="alert"` and are linked with `aria-describedby`.
