
## 2024-06-23 - Missing Screen Reader Links in Custom Form Components
**Learning:** The project's custom React Hook Form layouts routinely rely on adjacent `<label>` and `<Input>` components without explicit linking, causing screen readers to lose context. Validation errors also lack proper aria roles.
**Action:** Always map `htmlFor` on labels to `id` on inputs, and attach validation errors to inputs using `aria-invalid`, `aria-describedby`, and `role="alert"` on error elements.
