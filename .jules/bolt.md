## 2025-03-01 - Consolidate dashboard-style queries
**Learning:** In dashboard-style API endpoints (like `wizard_summary`), executing multiple individual database queries (e.g., `count()`, `first()`, `exists()`) sequentially creates severe N+1 style round-trip performance bottlenecks.
**Action:** Consolidate independent counts and existence checks into a single database round-trip by wrapping `func.count()`, `exists()`, and specific column selects in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
