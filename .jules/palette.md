## 2025-02-23 - Accessible Forms in React Hook Form
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), relying purely on visual proximity fails screen reader accessibility since the input has no associated accessible name and errors aren't announced.
**Action:** Explicitly link pairs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
