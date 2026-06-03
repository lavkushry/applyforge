## 2024-05-18 - Optimized Dashboard Endpoints
**Learning:** Found an opportunity to consolidate multiple independent counts and existence checks into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
**Action:** Used `scalar_subquery()` to batch independent queries.
