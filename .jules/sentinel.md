## $(date +%Y-%m-%d) - Removed hardcoded secrets from config and enforced security in seed/bootstrap

**Vulnerability:** Found hardcoded `secret_key` ("applyforge-dev-secret") and `bootstrap_default_user_password` ("defaultuser123") in `apps/api/app/core/config.py`.
**Learning:** These were left as convenient defaults for local development but pose a critical security risk if the application is deployed to production without overriding them.
**Prevention:** Used Pydantic `Field(...)` to make `secret_key` mandatory. Made `bootstrap_default_user_password` optional (`str | None = None`) but added runtime checks (`ValueError`) in `db/seed.py` and `services/bootstrap.py` to ensure a password is provided when a default user is actually being created. This "fails fast" and ensures missing configuration leads to a secure failure rather than an insecure default state.
