## 2024-06-19 - Skip Redundant DB Query During Job Ingestion
**Learning:** When processing loops in `company_ingestion.py`, we shouldn't hit the database to resolve companies if the current job's company matches the target `company` object already residing in memory.
**Action:** Implement an early return/bypass for database lookups in loops when the required target entity is already available in the execution context.
