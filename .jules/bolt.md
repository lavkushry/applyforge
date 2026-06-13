## 2024-06-13 - Dashboard N+1 Queries
**Learning:** Consolidating multiple independent count and existence checks into a single database round-trip via `scalar_subquery()` and `.limit(1)` in SQLAlchemy significantly reduces query overhead for dashboard-style endpoints (like `wizard_summary`).
**Action:** Consolidate multiple queries into a single query using `select()` and `scalar_subquery()` where appropriate.
