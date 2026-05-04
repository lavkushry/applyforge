
## 2026-05-04 - Consolidating Database Queries for Dashboard Endpoints
**Learning:** Multiple independent counts and existence checks (N+1 database queries) in dashboard endpoints like `wizard_summary` cause redundant database round-trips.
**Action:** Use SQLAlchemy's `scalar_subquery()` and `exists()` to consolidate these metrics into a single unified `select()` query, which reduces database round-trips and improves response times for dashboard-style endpoints.
