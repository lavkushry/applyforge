## 2024-06-25 - Missing Form Label Bindings
**Learning:** Widespread missing `htmlFor`/`id` bindings connecting labels to inputs, and missing `aria-describedby` and `aria-invalid` attributes linking inputs to validation errors in forms.
**Action:** Always use `useId()` (or explicitly passed IDs) to establish strict bindings between labels, inputs, and error messages for better accessibility. Add `role="alert"` to error messages.
