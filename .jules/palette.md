## 2024-05-25 - Missing form label and error bindings
**Learning:** React Hook Form usage in this codebase often neglects native HTML accessibility bindings (e.g., `htmlFor`, `id`, `aria-invalid`, `aria-describedby`, and `role="alert"`), making forms difficult to use with screen readers.
**Action:** When working with forms or adding new inputs, always generate a unique ID (using `useId`) and explicitly bind labels to inputs and errors to inputs to ensure full accessibility compliance.
