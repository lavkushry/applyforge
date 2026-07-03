## 2024-07-03 - [AuthForm] Add ARIA mapping for React Hook Form errors
**Learning:** Explicitly map form validation errors to their corresponding inputs for screen reader support using React Hook Form state. Adjacent elements require explicit `htmlFor` and `id` linking.
**Action:** Ensure custom forms manually link `<label>` and `<Input>` using `htmlFor` and `id`. Also map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` directly onto the error message element.
