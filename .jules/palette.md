## 2024-07-07 - Add accessibility attributes to form fields
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), explicitly linking pairs using `htmlFor` and `id`, and explicitly mapping validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` is critical for screen reader accessibility.
**Action:** Always link form labels to inputs and properly associate error messages using ARIA attributes when building custom form layouts.
