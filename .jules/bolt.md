## 2025-02-13 - Dashboard Query Consolidation
**Learning:** In dashboard-style endpoints doing independent counts and checks, making separate `db.query().count()` and `db.query().exists()` calls leads to multiple network roundtrips to the database which increases latency.
**Action:** Consolidate these independent queries into a single database roundtrip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()`. Ensure each scalar subquery limits to 1 row and 1 column.
