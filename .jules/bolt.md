## 2024-05-14 - Consolidate Independent Database Queries with Scalar Subqueries
**Learning:** Dashboard-style endpoints (like wizard_summary) often perform multiple independent `func.count()`, `.first()`, or `exists()` database queries, leading to many separate round-trips.
**Action:** Consolidate these independent count and existence checks into a single database round-trip by wrapping them in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
