## 2024-12-14 - React Hook Form Accessibility
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), missing explicit links prevent screen readers from associating labels and validation errors with inputs.
**Action:** Always explicitly link pairs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` to ensure screen reader accessibility.
