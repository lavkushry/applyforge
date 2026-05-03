## 2024-05-24 - Unauthenticated Diagnostic Endpoint Leak
**Vulnerability:** The `/admin/health` endpoint exposed backend diagnostic information (database and Redis availability) without requiring authentication.
**Learning:** Endpoints grouped in an 'admin' router or logically related to system diagnostics must explicitly include authentication dependencies (like `Depends(get_current_user)`), as the FastAPI router itself did not enforce this globally.
**Prevention:** Always verify that every route inside an authenticated module explicitly implements the required `Depends` injection, or attach the dependency directly to the `APIRouter` declaration to enforce it across all endpoints.
