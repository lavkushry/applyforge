# ApplyForge Deployment Guide

This guide outlines the standard procedures for deploying ApplyForge.

## Deployment Posture

ApplyForge currently supports two primary deployment topologies:

1. **Local or Staging Deployment:** Utilizing Docker Compose for rapid provisioning.
2. **Single-VM Production-Style Deployment:** A consolidated server running the service stack.

*Note: The `docker-compose.yml` file located in `infra/` is currently optimized for development (e.g., it mounts source code, uses `.env.example` files, runs the Next.js dev server, and triggers `create_all` for the database schema on startup). It must be adapted with override configurations for true production use.*

## Runtime Services

The ApplyForge architecture relies on five core runtime services:

- **`web`**: Next.js frontend application (Port `3000`)
- **`api`**: FastAPI backend service (Port `8000`)
- **`worker`**: Celery worker handling enrichment and application execution
- **`db`**: PostgreSQL 16 database
- **`redis`**: Redis 7 acting as the Celery broker and cache

*Optional tooling:*
- **`flower`**: Celery monitoring dashboard (Port `5555`)

---

## Environment Configuration

Before deploying, you must configure accurate environment files.

### 1. API Configuration

Copy the example file to create your active configuration:
`cp apps/api/.env.example apps/api/.env`

**Critical variables to update:**
- `ENV=prod`
- `WEB_ORIGIN=https://your-web-domain.com`
- `DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db>`
- `REDIS_URL=redis://<host>:<port>/0`
- `SECRET_KEY=<strong-random-secret>`
- `ACCESS_COOKIE_SECURE=true`
- `OPENAI_API_KEY=<real-key>`

**Inbox OTP Integration (Optional but recommended):**
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

### 2. Web Configuration

Copy the example file:
`cp apps/web/.env.example apps/web/.env.local`

**Critical variables to update:**
- `NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com`

### 3. Worker Configuration

Copy the example file:
`cp apps/worker/.env.example apps/worker/.env`

**Critical variables to update:**
- `DATABASE_URL=postgresql+psycopg2://...`
- `REDIS_URL=redis://...`
- `ARTIFACTS_PATH=/data/artifacts`
- `PLAYWRIGHT_HEADLESS=true`

---

## Deployment: Docker Compose (Staging/Local)

### 1. Prepare Environment
Ensure the three `.env` files detailed above have been created and populated.

### 2. Configure Compose Target
The default `infra/docker-compose.yml` points to `.env.example` files. For staging, you must either modify the `env_file` directives to point to your real `.env` files or provide a `docker-compose.override.yml`.

### 3. Start the Services
```bash
cd infra
docker compose up --build -d
```

### 4. Perform Smoke Checks
Verify the following endpoints are accessible:
- Web App: `http://localhost:3000`
- API Root: `http://localhost:8000/`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/admin/health` (Should return `{"status": "ok", "database": "ok", "redis": "ok"}`)
- Flower Dashboard: `http://localhost:5555`

---

## Deployment: Single-VM (Production-Style)

This approach is recommended for deploying to a single Linux host using Docker and a reverse proxy.

### Infrastructure Layout
- **Reverse Proxy:** Nginx, Caddy, or Traefik handling TLS termination.
- **Containers:** `web`, `api`, `worker`, `db`, `redis`.
- **Storage:** Persistent volumes mapped for PostgreSQL, file uploads, and worker artifacts.

### Persistent Volume Requirements
The API and Worker currently write directly to local disk storage. You must mount these directories to the host to prevent data loss:

- **Database:** `/srv/applyforge/postgres`
- **Uploads (`STORAGE_PATH`):** `/srv/applyforge/uploads`
- **Artifacts (`ARTIFACTS_PATH`):** `/srv/applyforge/artifacts`

### Reverse Proxy Routing
Route traffic securely using the following recommended pattern:
- `https://app.example.com` → Routes to the `web` container.
- `https://api.example.com` → Routes to the `api` container.

**Critical CORS and Cookie Settings:**
If utilizing HTTPS, you must ensure:
- `ACCESS_COOKIE_SECURE=true` is set in the API `.env`.
- `WEB_ORIGIN` precisely matches the public frontend URL.
*Note: The API derives its CORS policy strictly from the `WEB_ORIGIN` variable.*

### Rollout Sequence
1. Provision host storage directories and start PostgreSQL and Redis containers.
2. Deploy the `api` container with production environment variables and mounted storage.
3. Deploy the `worker` container, ensuring it shares the DB connection and artifact paths.
4. Deploy the `web` container configured with the public `NEXT_PUBLIC_API_BASE_URL`.
5. Execute the Post-Deploy Validation Checklist.

---

## OAuth and Inbox Integrations

If Inbox OTP support is required, the OAuth provider configurations must perfectly match your public API routing.

**Required Redirect URIs:**
- Google: `https://api.example.com/inbox/gmail/oauth/callback`
- Microsoft: `https://api.example.com/inbox/outlook/oauth/callback`

**Required Provider Scopes:**
- **Gmail:** `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- **Outlook:** `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

---

## Post-Deploy Validation Checklist

Following any deployment, execute these checks to ensure system integrity:

1. [ ] Access the landing page and authenticate.
2. [ ] Verify `GET /` and `GET /docs` respond correctly on the API host.
3. [ ] Verify `GET /admin/health` confirms DB and Redis are `ok`.
4. [ ] Upload a resume and confirm the profile parser executes successfully.
5. [ ] Create a target role, run a scrape, and confirm jobs populate the feed.
6. [ ] Confirm newly discovered jobs transition into a `pending` or `completed` enrichment state.
7. [ ] Tailor a resume against a job and successfully export the PDF.
8. [ ] Initiate a draft or assisted application run and confirm step logs are generated.
9. [ ] (If configured) Connect a Gmail or Outlook account via the Settings page.

---

## Observability and Operations

### Logging
Monitor the following signals during operations:
- API request-scoped structured logs (watch for auth, inbox, or file export failures).
- Worker logs (watch for Playwright launch failures or enrichment timeouts).
- Application run diagnostics available at `/admin`.

### Backup Procedures
To ensure complete data recovery, you must back up:
1. The PostgreSQL database data directory.
2. The `STORAGE_PATH` directory (contains uploaded resumes and exported PDFs).
3. The `ARTIFACTS_PATH` directory (contains run evidence, step logs, and screenshots).

*Note: Losing the `ARTIFACTS_PATH` data will result in missing screenshot evidence for historical application runs, though the run records themselves will remain in PostgreSQL.*

## Known Limitations and Future Hardening

Be aware of the following architectural gaps in the current release:

1. **Schema Management:** The API executes `Base.metadata.create_all(...)` on startup. Future releases must transition exclusively to Alembic migrations.
2. **Web Container Optimization:** The default web container utilizes `next dev`. A production deployment should utilize a dedicated `next build` and `next start` image.
3. **Storage:** Artifact and upload storage relies on local disk mapping. S3-compatible object storage integration is planned.
4. **Secret Management:** Secrets are currently managed via `.env` files rather than a dedicated secrets manager.
