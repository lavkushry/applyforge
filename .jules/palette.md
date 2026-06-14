## 2024-10-24 - Strict form a11y bindings
**Learning:** Forms lacked semantic label-to-input bindings and ARIA-based error associations, causing screen readers to miss input context and validation failures.
**Action:** Use `useId()` to generate deterministic IDs, explicitly connect `<label htmlFor>` to `<input id>`, and use `aria-describedby` pointing to error paragraphs with `role="alert"`.
