## 2025-02-18 - Optimized wizard_summary endpoint
**Learning:** Multiple existence and count checks can be consolidated into a single database round-trip by wrapping func.count() and exists() clauses in scalar_subquery() calls within a unified SQLAlchemy select() statement. exists() needs to be wrapped in a secondary select to avoid AttributeError.
**Action:** Always consolidate dashboard-style counts and exist checks into a single query using scalar_subquery() instead of running them individually.
