## 2024-05-15 - Consolidating API Endpoint Database Queries
**Learning:** Making multiple independent queries (`.first()`, `.count()`) in dashboard or summary endpoints creates unnecessary N+1 queries. We can wrap these as `scalar_subquery()` fields inside a single top-level `select()` to pull all the metadata in a single database round trip.
**Action:** Always look for multiple independent `.count()`, `.first()`, or `exists()` queries on a single object's dashboard routes and consolidate them via scalar subqueries.
