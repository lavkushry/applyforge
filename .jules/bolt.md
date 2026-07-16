## 2024-11-20 - Consolidate Independent Queries in Dashboard Endpoints
**Learning:** Multiple independent counts and existence checks in dashboard endpoints can create latency bottlenecks due to sequential DB roundtrips.
**Action:** Consolidate them into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement. Ensure the `exists()` is wrapped in a secondary select (e.g. `select(select(Model.id).where(...).exists())`) to avoid AttributeError.
