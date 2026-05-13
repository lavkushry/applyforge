## 2024-05-13 - Missing form label bindings
**Learning:** Across the application's forms, labels often lack `htmlFor`/`id` bindings connecting them to inputs, and inputs lack `aria-describedby` and `aria-invalid` attributes linking them to validation errors with `role="alert"`. This makes forms difficult to navigate and understand for screen reader users.
**Action:** Use `useId()` in React to establish strict bindings between labels, inputs, and error messages to ensure accessibility.
