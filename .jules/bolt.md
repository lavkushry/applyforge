## 2026-04-08 - Fixed N+1 in _serialize_role
**Learning:** Found an N+1 query pattern specific to the architecture when serialization functions like `_serialize_role` implicitly execute separate related-model queries inside loops on list routes.
**Action:** When a `_serialize_[entity]` function queries a `db`, add an optional `cache: dict | None = None` parameter and prefetch the related items via `in_` queries in list endpoints to batched process them instead of allowing O(N) queries per user row.
