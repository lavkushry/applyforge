## 2024-05-24 - Batch Prefetching in Ingestion Loops
**Learning:** Ingestion loops doing `.first()` lookups per job create massive N+1 bottlenecks in SQLAlchemy.
**Action:** Always use a two-pass pattern: collect/normalize all payloads to gather keys, batch query via `.in_(keys)`, and update the lookup cache inside the second loop after `db.flush()` to handle duplicates within the same run.
