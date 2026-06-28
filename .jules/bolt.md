## 2026-06-28 - Unified Queries via Scalar Subqueries
**Learning:** Multi-entity dashboard endpoints often cause an N+1-like issue by firing 6+ queries in succession. Using `scalar_subquery()` correctly allows fetching disparate existence checks and counts in a single database round-trip without cartesian product overhead.
**Action:** Use unified select statements wrapping counts and existence checks via `scalar_subquery()` for multi-metric dashboard-style API endpoints to cut down database calls.
