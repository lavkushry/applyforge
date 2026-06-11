## 2024-05-24 - Consolidating Database Queries
**Learning:** Dashboard-style endpoints like `wizard_summary` often make independent DB queries for multiple counts and checks (`func.count()`, `exists()`).
**Action:** Consolidate these independent counts and existence checks into a single database round-trip by wrapping them in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
