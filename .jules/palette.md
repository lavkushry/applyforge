## 2024-06-01 - Missing Form Label Bindings
**Learning:** React Hook Form fields frequently lack strict `htmlFor`/`id` bindings linking labels to inputs. Error messages are also often missing `aria-describedby`, `aria-invalid`, and `role="alert"`, degrading the screen reader experience.
**Action:** Use React's `useId()` hook to establish unique IDs and ensure labels, inputs, and error nodes are systematically interconnected to maintain full a11y compliance.
