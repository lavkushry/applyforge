## 2024-07-10 - Consolidate independent counts and exists checks
**Learning:** When optimizing dashboard-style endpoints in `apps/api` (e.g., `wizard_summary`), consolidate multiple independent counts and existence checks into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
**Action:** Look for multiple `.first()` and `.count()` database calls in endpoint functions and refactor them to use unified queries with `scalar_subquery()`.
