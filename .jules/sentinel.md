## 2024-05-24 - Missing Auth on Health Endpoint
**Vulnerability:** The `/admin/health` endpoint exposes system diagnostics (Redis and database status) without requiring authentication.
**Learning:** Endpoints exposing infrastructure status can leak internal info if not protected, even if grouped in an admin router.
**Prevention:** Always secure diagnostic endpoints with `Depends(get_current_user)` when they are part of a protected module or expose internal state.
