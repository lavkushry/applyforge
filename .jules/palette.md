## 2024-11-20 - Auth Form Accessibility

**Learning:** Forms in `apps/web/components/forms/` such as the authentication form lack proper accessibility attributes connecting labels, inputs, and validation errors, which makes them less accessible for screen readers. Missing bindings like `htmlFor` on `<label>` elements matching input `id`s, `aria-invalid` based on form error state, and `aria-describedby` linking the input to its corresponding error message that is styled as `role="alert"` can hide context and feedback from users relying on assistive technology.

**Action:** Whenever modifying forms, or adding new ones, use `useId()` to generate unique ids that link `<label>` elements with their `<input>` elements. Use `aria-invalid={!!error}` on inputs along with `aria-describedby` set to the id of the error text element. The error text elements should utilize `role="alert"` so errors are properly announced.
