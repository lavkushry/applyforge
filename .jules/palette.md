## 2024-05-23 - Improve Form Accessibility With Strict Bindings

**Learning:** There is a widespread pattern in the `apps/web/components/forms/` components where form inputs lack `htmlFor` / `id` bindings connecting labels to inputs. Furthermore, `aria-describedby` and `aria-invalid` attributes linking inputs to validation errors equipped with `role="alert"` are absent.

**Action:** When updating or creating new forms, use `useId()` from `react` (or explicitly passed IDs) to establish strict semantic bindings. Apply `<label htmlFor={id}>`, `<input id={id}>`, `aria-invalid={!!error}`, and `aria-describedby={errorId}`. Ensure error messages have `id={errorId}` and `role="alert"` to notify assistive technologies.
