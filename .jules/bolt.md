## 2024-04-09 - N+1 Query Elimination in Serialization
**Learning:** In `apps/api`, `_serialize_[entity]` helper functions (e.g., `_serialize_role`, `_serialize_application`) are frequently used to attach related database records. When used inside list endpoints, these can cause N+1 database query problems. Use prefetching and pass an optional `cache` dictionary to these helpers to batch queries.
**Action:** When working on API endpoints that return lists of objects, check the `_serialize_` functions to ensure they support a `cache` dict to avoid N+1 issues.
