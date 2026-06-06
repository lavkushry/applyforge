# ApplyForge Deployment Manual

## Environments
ApplyForge can be run via:
1. Local/Staging using Docker Compose.
2. Single-VM setups for a more production-like footprint.

Currently, the `infra/docker-compose.yml` is tailored for development (e.g. running `npm run dev` for the frontend and using direct `.env.example` loads), so it should not be utilized in pure production environments without customization.

## Service Mapping
ApplyForge relies on the following services:
- **web**: Next.js (port `3000`)
- **api**: FastAPI (port `8000`)
- **worker**: Celery worker
- **db**: PostgreSQL 16
- **redis**: Redis 7
- **flower** (optional): Dashboard (port `5555`)

## Initial Setup
Before anything, setup the `.env` configurations from their respective `.env.example` templates:
1. `apps/api/.env` requires configurations for the database URL, Redis URL, JWT Secret Key, and provider credentials (like Gmail or Outlook).
2. `apps/web/.env.local` requires `NEXT_PUBLIC_API_BASE_URL`.
3. `apps/worker/.env` requires the database URL, Redis URL, artifact paths, and Playwright specifications.

## Docker Compose Execution
To boot up the stack for testing, run:
```bash
cd infra
docker compose up --build
```

You should then verify the health status by checking:
- Web: `http://localhost:3000`
- API Health: `http://localhost:8000/admin/health`
- Flower Dashboard: `http://localhost:5555`

## Single-VM Production Deployments
In a more rigid setup, utilize persistent volumes, reverse proxies, and production-ready images.
- Reverse Proxies (Nginx/Traefik) should route `app.example.com` to the frontend and `api.example.com` to the backend.
- Set `ACCESS_COOKIE_SECURE=true` in HTTPS environments.
- Verify that your API's `WEB_ORIGIN` precisely mirrors the web domain to avoid CORS failures.

## Post-Deploy Checks
1. Validate `/admin/health` reports all systems OK.
2. Ensure you can register and login.
3. Test a resume upload and role creation.
4. If configured, bind an OAuth integration (Google/Microsoft) and verify OTP access.
5. Review Celery logs to ensure background workers are polling queues properly.

## Production Gaps
- Schema migrations still utilize `Base.metadata.create_all(...)` on boot; transitioning to Alembic migrations is highly recommended.
- S3 object storage adapters should be preferred over local storage mounts.
- Next.js should run via `next build` and `next start`.