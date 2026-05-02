## 2024-05-02 - N+1 Queries in List Endpoints with Serializer Helpers
**Learning:** In `apps/api`, list endpoints utilizing `_serialize_[entity]` helpers (e.g., `_serialize_role`) intrinsically trigger N+1 database queries if the helper fetches relationships one-by-one.
**Action:** To resolve this, pass an optional `cache` dictionary to the helper containing pre-fetched relationships (e.g., using `.in_()`). Bulk-fetch all associated rows for the entire list in a single query, group them by the parent entity ID into the cache dictionary, and pass it to the serializer.
