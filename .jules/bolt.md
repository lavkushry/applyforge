## 2024-05-22 - Fix N+1 queries in list endpoints
**Learning:** In `apps/api`, list endpoints utilizing `_serialize_[entity]` helpers (e.g., `_serialize_application`, `_serialize_role`) intrinsically trigger N+1 database queries.
**Action:** To resolve, pass a `cache` dict to the helper containing pre-fetched relationships.
