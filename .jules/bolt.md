
## 2024-05-07 - Consolidate DB queries in wizard_summary endpoint
**Learning:** Dashboard endpoints like `wizard_summary` that perform multiple independent counts and existence checks can suffer from N+1 query patterns and slow performance due to excessive database roundtrips.
**Action:** Consolidate multiple independent queries into a single database roundtrip by wrapping `func.count()` and `exists()` clauses in `scalar_subquery()` calls within a unified SQLAlchemy `select()` statement.
