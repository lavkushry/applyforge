## 2026-04-06 - Enforce environment variables for secrets in config.py
**Vulnerability:** Hardcoded fallback values for `secret_key` and `bootstrap_default_user_password` in `apps/api/app/core/config.py` could allow applications to run insecurely if these configurations are forgotten.
**Learning:** Hardcoded fallbacks make it easy to start the service but defeat the purpose of forcing explicit security configurations in higher environments, particularly in a Pydantic `BaseSettings` setup.
**Prevention:** Always use `Field(...)` for secrets in `BaseSettings` to ensure the application fails fast during initialization if the environment is incorrectly configured.
