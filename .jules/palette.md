## 2024-07-15 - Unlinked Form Labels and Errors
**Learning:** The application uses custom form layouts with React Hook Form where `<label>`, `<Input>`, and error messages are visually adjacent but programmatically unlinked, breaking screen reader association for validation states.
**Action:** Always explicitly link `<label htmlFor="x">` to `<Input id="x">`, and use `aria-invalid` / `aria-describedby` to map React Hook Form validation errors to the input elements.
