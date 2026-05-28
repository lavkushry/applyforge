## 2024-05-28 - Add ARIA accessibility to forms
**Learning:** React hook forms without strict `id` and `htmlFor` bindings fail to associate labels with inputs properly for screen readers. Using `aria-invalid` and `aria-describedby` linked to an element with `role="alert"` improves error reporting.
**Action:** Always utilize `useId()` to generate unique IDs for form fields, and properly link `htmlFor`, `id`, `aria-describedby`, and error IDs when building components in this app's forms.
