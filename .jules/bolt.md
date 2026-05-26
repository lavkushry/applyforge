## 2024-05-26 - Eliminate N+1 query in list serialization endpoint
**Learning:** List endpoints utilizing `_serialize_[entity]` helpers (like `_serialize_role`) intrinsically trigger N+1 database queries when they fetch related entities (like `TargetRoleSource`) separately for each item in the loop.
**Action:** Consolidate data access by fetching all required relationships ahead of time using `.in_(item_ids)` within the list endpoint, storing them in a `cache` dict, and passing that cache to the serialization helper.
