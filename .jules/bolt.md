## 2024-05-24 - Consolidated Dashboard Queries
**Learning:** Multiple independent `db.query().first()` and `db.query().count()` calls on dashboard endpoints create severe N+1 roundtrip overhead. Wrapping them in a single `select()` via `scalar_subquery()` correctly groups these lookups into a single SQL transaction query, significantly speeding up route latency.
**Action:** When a route performs 3+ distinct lookups (like count, exist checks, profile fetches) that do not depend on one another, always consolidate them into a single round-trip using `scalar_subquery()`.
