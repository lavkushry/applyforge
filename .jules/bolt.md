## 2024-06-10 - Dashboard Endpoint Query Consolidation
**Learning:** Dashboard-style endpoints (like `wizard_summary`) often make multiple independent database queries for counts and existence checks, causing unnecessary network overhead and latency.
**Action:** Consolidate these independent counts and existence checks into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
