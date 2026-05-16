## 2024-05-16 - Consolidating Dashboard Queries with scalar_subquery()
**Learning:** Dashboard-style endpoints often run multiple independent counts and exists checks sequentially, leading to an N+1 style query issue (N independent round trips) which can degrade performance.
**Action:** Consolidate multiple independent `func.count()` and `exists()` checks into a single database round-trip by wrapping them in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
