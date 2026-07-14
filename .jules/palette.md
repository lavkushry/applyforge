## 2024-05-19 - Explicitly Link React Hook Form Components for Screen Readers
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), simply placing a label next to an input is insufficient for screen readers. Validation errors also fail to announce without ARIA mapping.
**Action:** Explicitly link pairs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` to ensure screen reader accessibility.
