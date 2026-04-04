## 2025-01-20 - N+1 Serialization in FastAPI Endpoints
**Learning:** In `apps/api`, `_serialize_[entity]` helper functions (e.g., `_serialize_role`) cause N+1 database queries when called from list endpoints because they lazy-load related records (like `TargetRoleSource`) individually per parent entity.
**Action:** When working on list endpoints, preemptively query and batch related records in memory before passing them to the serialization function as optional arguments.
