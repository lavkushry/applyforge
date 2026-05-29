## 2026-05-29 - Optimize Dashboard Endpoints using Scalar Subqueries
**Learning:** Dashboard-style endpoints (like `wizard_summary`) that need multiple independent counts or boolean existence checks can cause N+1 query overhead.
**Action:** Consolidate multiple independent queries into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
