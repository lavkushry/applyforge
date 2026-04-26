## 2026-04-26 - Found unlinked form labels
**Learning:** Found several forms in the app where labels are not connected to inputs using htmlFor/id, and error messages lack aria-describedby for screen readers.
**Action:** Add id to inputs and htmlFor to labels. Add aria-describedby to inputs pointing to error message ids, and role='alert' to error messages.
