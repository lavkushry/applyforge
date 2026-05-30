## 2024-05-24 - N+1 Query in Company Ingestion Loop
**Learning:** During company portal scraping in `apps/api/app/services/company_ingestion.py`, calling `resolve_company_for_job` repeatedly in a loop caused an N+1 query problem, even though we already had the target `company` object loaded in memory.
**Action:** Always check if the object we are trying to resolve already matches an object we have in memory (like comparing `normalize_company_name(job_company_name) == company.normalized_name`) before executing a database query within a loop.
