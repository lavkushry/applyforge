## 2024-07-11 - Custom React Hook Form accessibility
**Learning:** Custom React form layouts combining `<label>` and `<Input>` (often with React Hook Form) lack explicit associations, causing validation errors and fields to be inaccessible to screen readers.
**Action:** Always link adjacent `<label>` and `<Input>` pairs explicitly using `htmlFor` and `id`. Map validation errors explicitly using `aria-invalid`, `aria-describedby`, and `role="alert"`.
