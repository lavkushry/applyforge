## 2024-07-12 - Explicit Label Linking in Custom Input Components
**Learning:** Custom React Hook Form implementations with generic `<Input>` components lack automatic screen reader associations between labels, inputs, and error messages.
**Action:** Always use `htmlFor` and `id` to explicitly link labels to inputs, and use `aria-invalid` and `aria-describedby` with a `role="alert"` element to properly announce form validation errors.
