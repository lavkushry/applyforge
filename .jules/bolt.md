## 2025-01-14 - Batch Pre-fetching & Memory Caching in Ingestion
**Learning:** Ingestion loops can cause severe N+1 database queries when checking for existing jobs by `dedupe_key` or resolving company names.
**Action:** Use a two-pass pattern: collect keys, batch query via `.in_(keys)`, and update the lookup cache inside the loop after `db.add()`. Avoid redundant DB calls by checking if the payload's company name matches the target company already in memory.
