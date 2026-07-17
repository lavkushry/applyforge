## 2024-11-20 - Ensure focus-visible on custom interactive cards
**Learning:** Reusable UI components (like <Button>) and custom clickable cards (using <button>) often rely on hover states but neglect keyboard focus styling, making them invisible to keyboard-only users.
**Action:** Explicitly add `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950` to the className of all interactive elements.
