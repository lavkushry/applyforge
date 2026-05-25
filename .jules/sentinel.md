## 2024-05-15 - [Remove hardcoded default password for bootstrap user]
**Vulnerability:** A hardcoded default password (`defaultuser123`) was present in `apps/api/app/core/config.py` for the bootstrap user, potentially allowing attackers to exploit it if the environment is deployed without properly overriding it.
**Learning:** Hardcoding default values for sensitive fields in Pydantic `BaseSettings` configurations makes the codebase insecure by default.
**Prevention:** Always use `None` (or another appropriate sentinel value) as the default for sensitive configuration fields. Downstream services using these configurations should be updated to handle `None` values gracefully or explicitly fail when they are missing.
