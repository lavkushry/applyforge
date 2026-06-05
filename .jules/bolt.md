## 2024-06-05 - Dashboard N+1 Queries
**Learning:** Dashboard-style endpoints doing multiple independent aggregations (e.g., `func.count()`, `exists()`) can cause N+1 query-like issues (N independent queries).
**Action:** Consolidate these independent aggregations into a single round trip using SQLAlchemy's `scalar_subquery()` within a unified `select()` statement.
