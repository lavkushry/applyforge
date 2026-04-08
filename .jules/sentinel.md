## 2025-02-14 - Removed hardcoded secrets from configuration
**Vulnerability:** Found hardcoded `secret_key` and `bootstrap_default_user_password` directly in `apps/api/app/core/config.py`.
**Learning:** Hardcoding sensitive values in the Pydantic Settings fallback meant the API would boot securely, but fail open with unsafe defaults if environment variables weren't passed during production startup.
**Prevention:** Always declare sensitive keys in Pydantic `BaseSettings` using `Field(...)` to guarantee immediate fail-safe exceptions on startup if they are omitted.
