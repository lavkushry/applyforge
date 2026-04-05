## 2024-04-05 - Forms Label Binding and ARIA Alerts
**Learning:** Found a widespread pattern across forms (like `auth-form.tsx`) where labels were missing `htmlFor` attributes to bind to inputs, and validation error messages lacked `role="alert"` and `aria-describedby` links. This negatively affects screen reader accessibility and the click target area for users.
**Action:** Always check form elements for `id`/`htmlFor` pairings, and ensure error messages utilize `role="alert"` alongside `aria-describedby` referencing the specific input field.
