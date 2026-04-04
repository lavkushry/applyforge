## 2024-04-04 - Unsafe Default Configurations
**Vulnerability:** The 'secret_key' and 'bootstrap_default_user_password' settings in `apps/api/app/core/config.py` use hardcoded, insecure defaults rather than enforcing environment variables.
**Learning:** This approach causes environments without explicitly set `.env` vars to fall back to using default credentials, resulting in unauthorized access or data exposure, as remembered in context memory.
**Prevention:** Use `pydantic.Field(...)` to declare sensitive fields as required, removing any default values. Doing so ensures the API cannot start without these variables properly set by an administrator.
