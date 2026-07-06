## 2024-05-24 - [Initial setup]
**Learning:** Checking UX layout across common form elements. React Hook Form is commonly used without proper accessible markup.
**Action:** Always check `htmlFor` on labels and aria attributes mapping to input IDs for validation errors.

## 2024-05-24 - [UX Layout and Forms]
**Learning:** React Hook form bindings are good but multiple components use standard `<label>` without `htmlFor` attributes, failing screen readers trying to link labels with inputs. Also standard `<input>` and `<select>` fields don't use the generated ID for their inputs to attach to labels.
**Action:** Always link `<label htmlFor="id">` and use `<Input id="id" />` for form elements to be fully accessible.
