## 2024-04-20 - Forms lack accessibility connections
**Learning:** This app's components have a widespread missing form label bindings pattern. Forms frequently omit `htmlFor` and `id` links between labels and inputs, and lack `aria-describedby` linking inputs to validation errors with `role="alert"`.
**Action:** Always verify form inputs have standard accessible connections (label bindings and aria attributes) when making form modifications or building new forms.
