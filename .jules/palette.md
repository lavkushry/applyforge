## 2024-05-24 - React Hook Form Accessibility
**Learning:** Custom React Hook Form layouts using adjacent `<label>` and `<Input>` components in this app lack implicit associations, causing screen readers to miss field names and validation errors.
**Action:** Explicitly link labels using `htmlFor`/`id` pairs and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
