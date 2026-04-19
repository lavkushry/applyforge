## 2024-05-14 - Prevent N+1 queries in _serialize_ routes

**Learning:** Endpoints in `apps/api` using `_serialize_[entity]` helpers typically cause N+1 queries if relationships aren't pre-fetched. When doing this, we must initialize the cache dictionary with empty collections for all IDs to prevent fallback SQL queries when relations are non-existent.

**Action:** Whenever optimizing `_serialize_[entity]` routes, modify the helper to accept an optional cache dictionary, collect all entity IDs in the route, pre-fetch relationships using `.in_()`, properly populate the cache dictionary with empty lists/Nones as a default, and then pass this mapped dictionary to the serialization loop.
