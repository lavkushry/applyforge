## 2024-06-27 - Form Field Accessibility Mapping
**Learning:** Custom React Hook Form setups with decoupled `<label>` and `<Input>` components require manual wiring. Errors without `role="alert"` and `aria-describedby` are effectively invisible to screen readers, and isolated labels need `htmlFor`/`id` pairs to be focusable.
**Action:** Explicitly link labels/inputs using `htmlFor` and `id`, and explicitly map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
