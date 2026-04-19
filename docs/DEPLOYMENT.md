# ApplyForge Deployment Guide

## Deployment Posture

ApplyForge effectively supports two primary deployment modes:

1. Local or staging deployments using Docker Compose.
2. A single-VM production-style deployment maintaining the identical service split.

While runnable container definitions exist within `infra/`, the current `docker-compose.yml` is explicitly development-oriented:
- Source code is actively mounted into the containers.
- Example environment files are consumed directly.
- The web container runs via `npm run dev`.
- The API creates database tables at startup using `Base.metadata.create_all(...)`.

Consequently, Compose functions exceptionally well for staging and operator testing, but requires explicit overrides before serving as a hardened production artifact.

## Runtime Components

ApplyForge consists of five core runtime services:

- **`web`**: Next.js frontend operating on port `3000`.
- **`api`**: FastAPI backend service operating on port `8000`.
- **`worker`**: Celery worker executing enrichment and applications.
- **`db`**: PostgreSQL 16 database.
- **`redis`**: Redis 7, serving as the Celery broker and cache.

*Optional Service:*
- **`flower`**: Celery dashboard operating on port `5555`.

## Environment Configuration

Always provision real environment files prior to deployment.

### API Environment
Begin with `apps/api/.env.example`.

**Critical Overrides:**
- `ENV=prod`
- `WEB_ORIGIN=https://your-web-domain`
- `DATABASE_URL=postgresql+psycopg2://...`
- `REDIS_URL=redis://...`
- `SECRET_KEY=<strong-random-secret>`
- `ACCESS_COOKIE_SECURE=true`
- `OPENAI_API_KEY=<real-key>`

*If enabling inbox OTP support, append:*
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

### Web Environment
Begin with `apps/web/.env.example`.

**Critical Overrides:**
- `NEXT_PUBLIC_API_BASE_URL=https://your-api-domain`

### Worker Environment
Begin with `apps/worker/.env.example`.

**Critical Overrides:**
- `DATABASE_URL=postgresql+psycopg2://...`
- `REDIS_URL=redis://...`
- `ARTIFACTS_PATH=/data/artifacts`
- `PLAYWRIGHT_HEADLESS=true`

## Staging Deployment (via Compose)

### 1. Provision Environment Files
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```
Ensure you populate these with valid, real values.

### 2. Override Compose References
The default `infra/docker-compose.yml` directly references `.env.example` files. You must update these `env_file` directives to point to your genuine `.env` files, or create a `docker-compose.override.yml` doing so.

### 3. Launch the Stack
```bash
cd infra
docker compose up --build
```

### 4. Perform Smoke Checks
Verify the following endpoints respond correctly:
- Web interface: `http://localhost:3000`
- API root: `http://localhost:8000/`
- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/admin/health` (Expect: `status=ok`, `database=ok`, `redis=ok`)
- Flower dashboard: `http://localhost:5555`

## Single-VM Production Deployment

Ideal for a solitary Linux host running Docker behind a reverse proxy.

### Recommended Topology
- Reverse Proxy: Nginx, Caddy, or Traefik.
- Containers: `web`, `api`, `worker`, `db`, `redis`.
- Persistent Volumes: Database, uploads, and artifacts.

### Persistent Volume Requirements
The API and worker actively write to local storage. You must persistently mount:
- PostgreSQL data (e.g., `/srv/applyforge/postgres`)
- API `STORAGE_PATH` (e.g., `/srv/applyforge/uploads`)
- API & Worker `ARTIFACTS_PATH` (e.g., `/srv/applyforge/artifacts`)

### Routing Configuration
**Standard Public Routing:**
- `https://app.example.com` routes to the `web` container.
- `https://api.example.com` routes to the `api` container.

**Critical Sync Requirements:**
- `WEB_ORIGIN` must exactly match the public web domain.
- `NEXT_PUBLIC_API_BASE_URL` must point accurately to the public API domain.
- OAuth redirect URIs must align with the final public API callback routes.

### Security and CORS
For HTTPS environments:
- Enforce `ACCESS_COOKIE_SECURE=true`.
- The API explicitly derives CORS policies from `WEB_ORIGIN`. Mismatches here will fundamentally break authentication and browser-based API requests.

### Example Rollout Sequence
1. Provision PostgreSQL and Redis instances.
2. Deploy the API container with real environment variables and mounted storage.
3. Deploy the worker container, ensuring it shares the DB and artifact paths.
4. Deploy the web container referencing the public API URL.
5. Verify health via `/admin/health`.
6. Validate the user login flow.
7. Confirm the Celery worker correctly consumes jobs.
8. Test file uploads and resume PDF exports.
9. Verify role scraping and subsequent enrichment.

## OAuth Configuration Notes

Inbox OTP functionality strictly requires accurate public callback URLs.

**Standard Callback Patterns:**
- Google: `https://api.example.com/inbox/gmail/oauth/callback`
- Microsoft: `https://api.example.com/inbox/outlook/oauth/callback`

**Mandatory Provider Scopes:**
- Gmail: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- Outlook: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

*If these mismatch the provider app registration, inbox connection will invariably fail.*

## Post-Deploy Validation Checklist

1. Access the web landing page and dashboard.
2. Hit `GET /` and `GET /docs` on the API domain to confirm reachability.
3. Query `GET /admin/health` ensuring database and Redis reflect `ok`.
4. Successfully register or log in.
5. Upload a resume and verify profile record creation.
6. Create a target role and successfully trigger a scrape.
7. Confirm jobs populate with a `pending` or `completed` enrichment state.
8. Trigger a resume tailor and export the resulting PDF.
9. Initiate a draft/assisted application run and verify step logs generate.
10. If configured, connect an OAuth inbox provider via Settings.

## Observability & Operations

**Key Operational Signals:**
- Structured, request-scoped API logs.
- The `/admin/health` endpoint.
- Internal run diagnostics available in `/admin`.
- Application run retry metadata.
- Flower dashboard for worker visibility.

**Rollout Monitoring Priorities:**
- API logs detailing authentication, inbox, and file export failures.
- Worker logs tracking Playwright launch issues or enrichment crashes.
- PostgreSQL volume disk growth.
- Artifact directory growth (screenshots and enrichment captures).

## Disaster Recovery

Ensure robust backups exist for:
- PostgreSQL database data.
- Uploaded resumes/exported files located within `STORAGE_PATH`.
- Artifacts within `ARTIFACTS_PATH` (critical for run evidence and screenshots).

*Note: Losing artifact storage while retaining PostgreSQL preserves run records, but permanently destroys screenshot and export evidence.*

## Known Limitations

1. **Schema Migrations:** The API still initiates `Base.metadata.create_all(...)` during startup (`main.py`). Full reliance on Alembic migrations is incomplete.
2. **Compose Posture:** The committed Compose file remains strictly development-oriented and mandates overrides for production.
3. **Web Server:** The web container presently runs the Next.js dev server, not a finalized production build.
4. **Storage Mediums:** Storage strictly utilizes local disks; S3-compatible object storage is pending.
5. **Database Resets:** Older local databases may require destructive resets due to frequent developmental schema modifications.

## Hardening Priorities

Before undertaking a public launch, address these crucial steps:
1. Author an explicit, hardened production Compose file or deployment manifest.
2. Transition the web container to execute a production `next build` followed by `next start`.
3. Eliminate runtime `create_all` commands in favor of comprehensive Alembic migrations.
4. Migrate uploads and artifacts to durable S3-compatible object storage.
5. Implement TLS-terminated routing and transition secrets to an external secret manager.
