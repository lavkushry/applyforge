## 2024-06-19 - Accessible Form Validation
**Learning:** Custom `<label>` and `<Input>` components used with React Hook Form are not programmatically connected, breaking screen reader navigation. Validation errors also lack aria associations.
**Action:** Explicitly link label and input pairs using `htmlFor` and `id`, and always map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
