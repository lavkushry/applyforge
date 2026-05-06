## 2024-05-07 - Missing Authentication on Diagnostic Endpoints
**Vulnerability:** The `/health` endpoint in `admin.py` exposed database and Redis connectivity status to unauthenticated users.
**Learning:** Diagnostic or health endpoints, especially when grouped under admin-related route modules, are sometimes overlooked for authentication because they seem harmless, but they can leak internal infrastructure details.
**Prevention:** Always ensure that every endpoint within an authenticated router module (like `admin.py`) explicitly includes the required authentication dependency (e.g., `Depends(get_current_user)`), or apply the dependency at the router level.
