## 2024-07-16 - Explicitly linking labels to inputs in custom React forms

**Learning:** When using React Hook Form with separated label and input components, inputs fail to convey their purpose to screen readers without explicit `htmlFor` attributes on labels targeting input `id`s. Similarly, validation error messages need `role="alert"` and `aria-describedby` mapping to ensure they are immediately discoverable.
**Action:** Always ensure any `<label>` component uses `htmlFor` pointing to the corresponding `<input>`/`<Input>` id, and map any inline validation error tags using `aria-invalid` and `aria-describedby` on the input, and `role="alert"` on the error text element itself.
