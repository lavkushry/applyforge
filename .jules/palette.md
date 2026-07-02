## 2024-07-02 - React Hook Form Label Accessibility
**Learning:** Custom React form layouts with adjacent `<label>` and `<Input>` components need explicit `htmlFor` and `id` linking. Furthermore, mapping validation errors requires `aria-invalid`, `aria-describedby`, and `role="alert"` attributes to ensure proper screen reader support.
**Action:** Explicitly link labels and inputs using `htmlFor`/`id` and explicitly map validation errors using proper ARIA attributes when implementing custom forms.
