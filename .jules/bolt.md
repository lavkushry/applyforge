
## 2024-06-29 - Consolidating Database Queries with scalar_subquery
**Learning:** In dashboard-style endpoints like `wizard_summary` that perform multiple independent aggregations and existence checks, running them sequentially leads to N+1 query performance issues.
**Action:** Use SQLAlchemy's `scalar_subquery()` and `exists()` to wrap these independent counts into a single unified `select()` statement, reducing multiple database round-trips to one.
