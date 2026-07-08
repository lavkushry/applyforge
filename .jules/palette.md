## 2024-10-25 - Form Accessibility Improvements
**Learning:** In custom React form layouts (like those using React Hook Form), adjacent `<label>` and `<Input>` components lack automatic association, hindering screen reader usability. Form validation errors are also missed by assistive tech without proper ARIA attributes.
**Action:** Explicitly link form label/input pairs using `htmlFor` and `id`, and always map validation errors using `aria-invalid`, `aria-describedby`, and `role="alert"`.
