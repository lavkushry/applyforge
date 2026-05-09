## 2026-05-09 - Consolidating API dashboard queries with scalar subqueries
**Learning:** The setup wizard endpoint was making 6 separate database queries for counts and existence checks, causing unnecessary N+1 style latency.
**Action:** Use SQLAlchemy's `scalar_subquery()` and `exists()` to consolidate multiple independent counts into a single unified `select()` statement, executing them all in one database round-trip without needing full ORM models.
