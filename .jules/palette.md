## 2024-07-10 - Global Focus Indicators
**Learning:** Keyboard accessibility was missing a visual indicator for interactive elements (Buttons, Links), which degrades the experience for keyboard-only users.
**Action:** Added `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950` to the shared `Button` and `Nav` links. Apply this focus ring pattern to all new interactive components in the design system to ensure WCAG 2.4.7 compliance.
