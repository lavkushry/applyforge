## 2024-05-23 - Prevent N+1 queries in role serialization
**Learning:** List endpoints utilizing `_serialize_[entity]` helpers (like `_serialize_role`) trigger N+1 database queries when fetching relationships (like `TargetRoleSource`) individually.
**Action:** Consolidate multiple queries into a single round-trip by pre-fetching relationships in the list endpoint using `.in_()` for bulk ID lookup, grouping them into a dictionary by the parent ID, and passing this `cache` dictionary to the serialization helper.
