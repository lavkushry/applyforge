
## 2024-05-18 - Optimized wizard_summary Dashboard Endpoint
**Learning:** In dashboard endpoints that fetch multiple independent counts and existence checks (like `/setup/wizard`), executing multiple `.first()` and `.count()` queries creates unnecessary database round-trips. Grouping them via `scalar_subquery()` allows PostgreSQL to run them in a single query block, significantly boosting performance.
**Action:** Always refactor independent counts/exists checks on dashboards into a single query using `scalar_subquery()` when feasible.
