## 2026-06-26 - Form Input Accessibility
**Learning:** Custom React form layouts (specifically with React Hook Form) require explicit link mapping for accessibility, as adjacent labels and inputs are not automatically associated by screen readers.
**Action:** Explicitly link adjacent `<label>` and `<Input>` pairs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
