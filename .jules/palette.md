## 2024-10-24 - Explicit accessibility linkages in custom React Hook Form layouts
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), explicit linkage is often missed, reducing screen reader accessibility.
**Action:** Explicitly link pairs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"` to ensure proper context for assistive technologies.
