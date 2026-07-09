## 2024-07-09 - Accessible Form Components Pattern
**Learning:** Custom form layouts in ApplyForge using adjacent `<label>` and UI library `<Input>` components lose native programmatic association. Screen readers cannot properly identify inputs or announce validation errors without explicit mapping.
**Action:** When building forms in ApplyForge, explicitly pair `<label>` and `<Input>` using `htmlFor` and `id`. Route validation errors from React Hook Form to screen readers by applying `aria-invalid`, `aria-describedby` on the input, and `role="alert"` on the error text element.
