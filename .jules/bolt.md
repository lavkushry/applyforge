
## 2024-05-18 - Consolidating Dashboard Metrics with Scalar Subqueries
**Learning:** Dashboard-style endpoints (like `wizard_summary`) often suffer from N+1 or multiple sequential independent database query issues because they aggregate multiple separate counts and existence checks (e.g., jobs, roles, resumes) across different tables. Running these individually adds multiple round-trips to the database latency.
**Action:** When calculating multiple independent aggregates or fetching single properties for dashboard endpoints in `apps/api`, consolidate them into a single round-trip by wrapping `func.count()`, `exists()`, or direct column selections (with `.limit(1)`) inside `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
