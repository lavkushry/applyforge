## 2024-05-12 - Consolidate Multiple Dashboard Queries
**Learning:** Dashboard endpoints like `wizard_summary` in `apps/api` often make multiple independent sequential database queries for counts and existence checks (e.g., using `count()` and `first()`), leading to an N+1 query problem on page load.
**Action:** Use `scalar_subquery()` within a unified SQLAlchemy `select()` statement to consolidate multiple counts and existence checks into a single database round-trip. This avoids pulling full ORM objects into memory unnecessarily and speeds up dashboard load times.
