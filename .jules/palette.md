## 2024-05-27 - Form Binding Accessibility Missing
**Learning:** Found a recurring pattern in the app's components (like AuthForm) where form labels and inputs lack explicit `htmlFor` and `id` bindings, and validation error messages lack `aria-invalid` and `aria-describedby` with `role="alert"`. This makes forms difficult to navigate via screen readers.
**Action:** Use `useId()` to generate deterministic IDs for forms to properly link labels to inputs, and explicitly associate error messages with their respective input elements using `aria-describedby` and `aria-invalid` attributes.
