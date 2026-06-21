## 2024-05-18 - Accessibility improvements for React Hook Form inputs
**Learning:** When using adjacent `<label>` and custom `<Input>` components (like with React Hook Form), explicit linkage using `htmlFor` and `id` is crucial. Additionally, validation errors must be explicitly mapped using `aria-invalid`, `aria-describedby`, and `role="alert"` for screen reader accessibility.
**Action:** Always map the ID of the error message container to the `aria-describedby` attribute of the corresponding input field, and use `aria-invalid` to indicate validation failure dynamically.
