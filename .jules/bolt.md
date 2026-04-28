## 2024-04-28 - N+1 Query in Fastapi List Endpoints
**Learning:** List endpoints that use a `_serialize_[entity]` helper (like `_serialize_role`) will trigger N+1 database queries if relationships (like `TargetRoleSource`) are queried inside the helper.
**Action:** Always pre-fetch relations using `.in_()` in the main list route, build an in-memory dictionary grouped by the parent ID (handling missing relationships explicitly, like `[]` or a `is_fully_cached` flag), and pass this `cache` dictionary to the serializer helper to prevent fallback queries.
