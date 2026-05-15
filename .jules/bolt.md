## 2024-05-24 - Consolidate Multiple Dashboard DB Queries
**Learning:** Dashboard endpoints like `wizard_summary` often make many separate database queries (e.g., fetching profile, resume, inbox count, role count, job count) which can lead to high latency due to multiple round-trips.
**Action:** Consolidate these independent counts and existence checks into a single database round-trip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
