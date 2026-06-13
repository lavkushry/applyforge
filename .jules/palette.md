## 2024-05-15 - Missing ARIA Bindings in Forms
**Learning:** Forms within `apps/web/components/forms/` often lack `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` and `aria-invalid` attributes.
**Action:** Use `useId()` to establish strict bindings and add `role="alert"` to error messages.
