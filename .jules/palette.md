## 2024-12-05 - Form accessibility for React Hook Form
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), inputs and labels are disconnected, causing screen readers to fail.
**Action:** Always explicitly link pairs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` to ensure screen reader accessibility.
