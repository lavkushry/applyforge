## 2024-05-14 - Accessible Form Layouts
**Learning:** In custom React form layouts with adjacent `<label>` and `<Input>` components (like those used with React Hook Form), explicit mapping using `htmlFor` and `id` is required. Additionally, validation errors must be explicitly mapped using `aria-invalid`, `aria-describedby`, and `role="alert"` to ensure screen reader accessibility.
**Action:** Explicitly link labels and inputs, and map validation errors correctly in all future React hook form layouts.
