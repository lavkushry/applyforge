## 2024-05-15 - Unbound Form Labels and Error Messages
**Learning:** Found widespread accessibility pattern where form labels were not bound to their inputs via `htmlFor`/`id`, and validation error messages lacked `role="alert"` or `aria-describedby` connection to the invalid input.
**Action:** When working on form components, always bind `<label htmlFor="id">` to `<input id="id">` and use `aria-describedby` on inputs linking to a `role="alert"` element for displaying validation errors.
