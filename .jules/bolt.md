## 2024-07-15 - Consolidate query logic in wizard_summary
**Learning:** Consolidating multiple `db.query(...).count()` or `.first()` calls using `scalar_subquery()` heavily reduces the number of roundtrips to the DB. `exists()` needs to be wrapped in a secondary `select(...)` when used within `scalar_subquery()`.
**Action:** Always combine dashboard-style aggregate queries using scalar subqueries for better DB performance.
