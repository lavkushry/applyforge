## 2024-05-01 - Consolidating API dashboard queries
**Learning:** `apps/api` endpoints generating dashboard summaries (like `/setup/wizard`) can perform multiple independent N+1 counts/exists checks, causing overhead.
**Action:** Consolidate multiple independent `func.count()` and `exists()` checks into a single database round-trip by wrapping them in `scalar_subquery()` calls within a unified SQLAlchemy `select(...)` statement. This was verified to maintain all tests passing while reducing database queries.
