## 2024-06-22 - Prevent N+1 queries during company ingestion resolution
**Learning:** In `apps/api/app/services/company_ingestion.py`, redundant database calls to `resolve_company_for_job` occur for every job because passing `explicit_company_id` unconditionally triggers a DB query to fetch the company.
**Action:** Avoid redundant DB queries by checking if the job's company name matches the current target company already in memory, allowing for direct use of the existing object.
