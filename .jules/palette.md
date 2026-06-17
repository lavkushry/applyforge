## 2024-06-18 - Missing Form Label Associations & Keyboard Focus
**Learning:** Found an accessibility issue pattern across the app where `<label>` tags lack `htmlFor` attributes (breaking screen reader association and click-to-focus) and the core `<Button>` component lacked `focus-visible` styles (breaking keyboard navigation tracking).
**Action:** Always pair `<label htmlFor="id">` with `<Input id="id">`. Ensure interactive UI components have clear `focus-visible:ring-2` styles.
