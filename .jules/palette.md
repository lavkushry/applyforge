## 2024-11-20 - Explicit Form Accessibility Links
**Learning:** Custom React Hook Form layouts with adjacent labels and inputs lack automatic screen reader associations.
**Action:** Explicitly link pairs using `htmlFor` and `id`, and map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
