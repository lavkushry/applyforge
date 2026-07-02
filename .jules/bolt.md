## 2025-07-02 - Optimize wizard_summary database queries
**Learning:** Fetching multiple independent counts and existence checks via individual database queries or `.first()` calls causes unnecessary database round-trips.
**Action:** Consolidate them into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
