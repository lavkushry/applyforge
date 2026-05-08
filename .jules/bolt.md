## 2024-05-08 - Consolidation of Wizard Summary Queries
**Learning:** Multiple independent `count()`, `exists()`, and existence checks on the dashboard or wizard summary endpoints cause N+1 query patterns as they map to separate round-trips.
**Action:** Consolidate multiple counts and existence checks into a single round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a single SQLAlchemy `select()`. Array and JSON columns can also be extracted using `limit(1).scalar_subquery()` without instantiating complete ORM models.
