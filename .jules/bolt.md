## 2025-04-11 - Optimize API Serialization Endpoints with Pre-fetching

**Learning:** When creating `_serialize_[entity]` helper functions that query relationship tables for nested output data, utilizing them sequentially in list endpoints results in severe N+1 database querying issues (e.g., `list_roles` firing an individual query for `TargetRoleSource` on every single role).

**Action:** Whenever serializing a list of items that require relationships, collect the primary entity IDs, execute a single `.in_()` query to fetch all required relationships, group them into a dictionary by parent ID, and pass this dictionary to the serialization helper via an optional `cache: dict | None = None` parameter.
