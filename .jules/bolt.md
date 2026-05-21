## 2024-05-24 - Consolidate Multiple Dashboard Queries
**Learning:** In dashboard-style endpoints like `wizard_summary`, executing multiple independent `db.query(...).first()` or `count()` calls creates a significant N+1-like database round-trip bottleneck.
**Action:** Consolidate multiple independent counts and existence checks into a single database round-trip by wrapping `func.count()` and `exists()` clauses (or targeted column selects) in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
