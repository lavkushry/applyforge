## 2024-05-06 - Missing Form Label Bindings and Error Associations
**Learning:** Forms in `apps/web/components/forms/` often lack `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` linking inputs to validation errors equipped with `role='alert'`.
**Action:** Always include `htmlFor` on `<label>`, matching `id` on `<input>`, and conditionally render `aria-invalid` and `aria-describedby` when validation errors are present to improve screen reader accessibility.
