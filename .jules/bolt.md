## 2024-04-14 - Dashboard N+1 Fallbacks

**Learning:** When using bulk pre-fetching mechanisms (e.g. `_build_application_cache`) to avoid N+1 queries during serialization, simply executing bulk queries using `.in_()` is insufficient. If a relationship points to `None` (like `job.role_id` is missing) or there are zero associated children for a parent, the cache will be missing a key for that entity entirely. When the serializer attempts to `cache.get(id)`, it will miss, falling back to a direct SQL query, thus accidentally leaking N+1 queries.
**Action:** Always pre-seed the caching dictionary with the expected lookup keys explicitly mapping to `None` prior to updating the dictionary with fetched row entities.
