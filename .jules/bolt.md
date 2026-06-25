## 2024-05-20 - Consolidate Independent Counts via Scalar Subqueries
**Learning:** Sequential database queries for multiple independent counts and existence checks (e.g. for dashboard metrics) introduce major connection and parsing overhead latency.
**Action:** When building aggregate dashboard endpoints, consolidate independent `func.count()` and `exists()` queries into a single database round-trip using a unified SQLAlchemy `select()` wrapped with `scalar_subquery()`.
