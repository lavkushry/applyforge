## 2024-05-17 - Missing Form Label Bindings
**Learning:** Forms across `apps/web/components/forms/` lack `htmlFor`/`id` bindings connecting labels to inputs.
**Action:** Use `useId()` (or explicitly passed IDs, or field names as IDs) to establish strict bindings. The `FieldError` component (e.g., in `profile-form.tsx`) accepts an `id` prop to facilitate `aria-describedby` references. Address these a11y gaps when modifying components.
