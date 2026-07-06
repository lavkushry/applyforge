# ApplyForge Production Deployment

## Operational Posture
ApplyForge can currently be deployed in two primary ways:
1. Docker Compose (suitable for local testing and staging environments)
2. Single-VM Dockerized setup (suitable for early-stage production)

The configuration provided in `infra/` is currently tailored for development (e.g., volume mounts for source code, `npm run dev` for the frontend, and auto-creation of database schemas). For production, these defaults must be heavily modified.

## System Architecture
The deployment consists of five core services:
- **Web Frontend (`web`):** Next.js instance on port `3000`
- **Backend API (`api`):** FastAPI instance on port `8000`
- **Task Processor (`worker`):** Celery/Playwright runtime
- **Database (`db`):** PostgreSQL 16 instance
- **Cache & Broker (`redis`):** Redis 7 instance
- **Monitoring (Optional, `flower`):** Celery dashboard on port `5555`

## Environment Variable Preparation
Before launching, you must provision concrete environment configurations.

### API Configuration (`apps/api/.env`)
Copy `apps/api/.env.example` and strictly define:
- `ENV=prod`
- `WEB_ORIGIN=https://<your-frontend-domain>`
- `DATABASE_URL=postgresql+psycopg2://<credentials>`
- `REDIS_URL=redis://<credentials>`
- `SECRET_KEY=<cryptographically-secure-string>`
- `ACCESS_COOKIE_SECURE=true`
- `OPENAI_API_KEY=<active-key>`

*(OAuth variables like `GOOGLE_OAUTH_CLIENT_ID` and `MICROSOFT_OAUTH_CLIENT_ID` are required if OTP retrieval is enabled).*

### Web Configuration (`apps/web/.env.local`)
Copy `apps/web/.env.example` and define:
- `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-domain>`

### Worker Configuration (`apps/worker/.env`)
Copy `apps/worker/.env.example` and define:
- `DATABASE_URL` (same as API)
- `REDIS_URL` (same as API)
- `ARTIFACTS_PATH=/data/artifacts`
- `PLAYWRIGHT_HEADLESS=true`

## Compose Staging Deployment
If deploying via Compose, ensure you duplicate the `.env.example` files to their real counterparts, as the default [docker-compose.yml](../infra/docker-compose.yml) natively points to `.env.example`.

To launch:
```bash
cd infra
docker compose up --build
```
Verify health via `http://localhost:8000/admin/health` (should return `{status: ok, database: ok, redis: ok}`).

## Single-VM Production Deployment
For a standard production setup on a single Linux host, utilize a reverse proxy (Nginx, Caddy, or Traefik) to route traffic to the Docker containers.

### Storage Requirements
The API and Worker require durable local disk access. Mount these paths securely to the host:
- PostgreSQL Data: e.g., `/srv/applyforge/postgres`
- User Uploads: e.g., `/srv/applyforge/uploads` (maps to `STORAGE_PATH`)
- Run Artifacts: e.g., `/srv/applyforge/artifacts` (maps to `ARTIFACTS_PATH`)

### Proxy and Domain Routing
- Route `https://<frontend-domain>` to the `web` container.
- Route `https://<backend-domain>` to the `api` container.

Ensure `WEB_ORIGIN` precisely matches the frontend domain, as the backend relies on this for CORS enforcement. Mismatches will immediately break authentication.

### Network Port Reference
- API: `8000` (HTTP)
- Web: `3000` (HTTP)
- Flower: `5555` (HTTP)
- Redis: `6379` (TCP)

### Suggested Rollout Sequence
1. Initialize PostgreSQL and Redis.
2. Boot the API container with mounted storage.
3. Boot the Worker container connected to the same DB/Artifact paths.
4. Boot the Web container pointing to the public API domain.
5. Validate `/admin/health`.
6. Test authentication, file uploads, and background enrichment tasks.

## Production OAuth Considerations
If integrating Gmail or Outlook for OTP scraping, your provider application must explicitly whitelist your production API callback URIs:
- Google: `https://<backend-domain>/inbox/gmail/oauth/callback`
- Microsoft: `https://<backend-domain>/inbox/outlook/oauth/callback`

The required OAuth scopes include profile and email reading permissions. Missing scopes will break the integration silently.

## Operational Validation
Post-deployment, always verify:
1. Web UI is accessible.
2. API root (`/`) returns successfully.
3. Authentication flows function properly.
4. Uploading a resume parses correctly.
5. Target role discovery enriches jobs successfully.
6. Tailored PDF generation succeeds.
7. Application run execution logs correctly.

## Monitoring and Backups
Monitor API request logs, Flower for Celery tasks, and disk space (especially artifact storage).

At a minimum, implement automated backups for:
- PostgreSQL volumes
- `STORAGE_PATH` (resumes)
- `ARTIFACTS_PATH` (screenshots and evidence logs)

## Current Limitations to Address
For true enterprise production, you will need to resolve these current MVP limitations:
1. The API relies on `create_all` for schema generation; migrate this to proper Alembic scripts.
2. The frontend container runs Next.js in dev mode; transition this to a compiled `next build` artifact.
3. File storage is tightly coupled to the local filesystem; S3 integration is recommended.
4. Introduce a dedicated production Docker Compose manifest.
