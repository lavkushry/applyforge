## 2024-04-03 - Missing Form Label and Error Associations
**Learning:** Across the codebase, custom form components (like `Input`) and error messages are often missing `htmlFor`, `id`, `aria-describedby`, and `aria-invalid` bindings, reducing screen reader accessibility. Error messages lacked `role="alert"` for immediate feedback.
**Action:** Always associate labels with inputs using `htmlFor` and `id`. Provide inline validation errors an `id` that is referenced by the input's `aria-describedby` attribute, set `aria-invalid`, and ensure error containers have `role="alert"`.
