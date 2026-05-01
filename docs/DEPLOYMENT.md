# ApplyForge Deployment Guide

## 🚀 Deployment Posture

ApplyForge currently supports two primary deployment modes:

1. **Local or Staging Deployment:** Utilizing Docker Compose for rapid iteration and testing.
2. **Single-VM Production-Style Deployment:** A more robust setup utilizing the same service split on a dedicated host.

**⚠️ Important Caveat:** The Docker Compose file provided in `infra/` is currently optimized for *development*. It mounts source code directly into containers, references local `.env.example` files, runs the Next.js development server (`npm run dev`), and relies on the FastAPI backend to create database tables at startup. While excellent for staging, it **must** be overridden with production-ready configurations before facing public traffic.

---

## 🏗️ Runtime Components

ApplyForge consists of five core runtime services:

- **`web`**: Next.js frontend running on port `3000`.
- **`api`**: FastAPI backend service running on port `8000`.
- **`worker`**: Celery worker responsible for data enrichment and Playwright application execution.
- **`db`**: PostgreSQL 16 database.
- **`redis`**: Redis 7, serving as both the Celery broker and system cache.

*Optional Component:*
- **`flower`**: Celery monitoring dashboard running on port `5555`.

---

## 🔐 Required Environment Files

Before deploying in any mode, you must provision actual environment variables.

### API Environment (`apps/api/.env`)
Begin by copying `apps/api/.env.example`.

**Critical Overrides:**
- `ENV=prod`
- `WEB_ORIGIN=https://your-web-domain.com` (Crucial for CORS)
- `DATABASE_URL=postgresql+psycopg2://<user>:<pass>@db:5432/<dbname>`
- `REDIS_URL=redis://redis:6379/0`
- `SECRET_KEY=<generate-a-strong-random-secret>`
- `ACCESS_COOKIE_SECURE=true` (Required for HTTPS deployments)
- `OPENAI_API_KEY=<your-real-key>`

*Optional: Inbox OTP Integrations*
If enabling Inbox OTP functionality, you must configure your OAuth providers:
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

### Web Environment (`apps/web/.env.local`)
Begin by copying `apps/web/.env.example`.

**Critical Overrides:**
- `NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com`

### Worker Environment (`apps/worker/.env`)
Begin by copying `apps/worker/.env.example`.

**Critical Overrides:**
- `DATABASE_URL=postgresql+psycopg2://<user>:<pass>@db:5432/<dbname>`
- `REDIS_URL=redis://redis:6379/0`
- `ARTIFACTS_PATH=/data/artifacts`
- `PLAYWRIGHT_HEADLESS=true` (Must be true for server environments)

---

## 💻 Local or Staging Deployment (Docker Compose)

### 1. Prepare Environment Files
Initialize your local secrets:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```
*Be sure to populate these with valid test keys (e.g., OpenAI API).*

### 2. Address Compose Limitations
The default `infra/docker-compose.yml` is hardcoded to reference `*.env.example` files. For a true staging test, manually update the `env_file` directives in `docker-compose.yml` (or create a `docker-compose.override.yml`) to point to your newly created real `.env` files.

### 3. Launch the Stack
```bash
cd infra
docker compose up --build
```

### 4. Perform Smoke Checks
Verify service health:
- **Web UI:** `http://localhost:3000`
- **API Root:** `http://localhost:8000/`
- **API Swagger Docs:** `http://localhost:8000/docs`
- **System Health:** `http://localhost:8000/admin/health` *(Expected output: `status=ok`, `database=ok`, `redis=ok`)*
- **Flower Dashboard:** `http://localhost:5555`

---

## 🌍 Single-VM Production-Style Deployment

Use this architecture when deploying to a single Linux host equipped with Docker and a reverse proxy.

### Recommended Layout
- **Reverse Proxy:** Nginx, Caddy, or Traefik.
- **Containers:** Run `web`, `api`, `worker`, `db`, and `redis` as separate containers.
- **Volumes:** Utilize persistent Docker volumes or host mounts for critical data.

### Persistent Volume Paths
The API and Worker write critical operational evidence directly to local storage. You *must* map these to persistent host directories:
- **Database:** `/srv/applyforge/postgres`
- **API Uploads (`STORAGE_PATH`):** `/srv/applyforge/uploads`
- **Artifacts (`ARTIFACTS_PATH`):** `/srv/applyforge/artifacts` (Shared between API and Worker)

### Reverse Proxy Routing Guidelines
Set up your proxy to route traffic cleanly:
- `https://app.your-domain.com` ➡️ Routes to the Web container (Port 3000)
- `https://api.your-domain.com` ➡️ Routes to the API container (Port 8000)

**Critical Alignment Checks:**
- The API's `WEB_ORIGIN` env var must perfectly match the Web app's public URL (for CORS).
- The Web's `NEXT_PUBLIC_API_BASE_URL` env var must resolve to the API's public URL.
- OAuth redirect URIs registered with Google/Microsoft must precisely match the API's public callback URLs.

### Security Configurations
For HTTPS deployments, strict security settings are required:
- Set `ACCESS_COOKIE_SECURE=true` in the API.
- Ensure CORS mappings (`WEB_ORIGIN`) are exact.

### Example Rollout Sequence
1. Provision host and initialize PostgreSQL/Redis containers.
2. Deploy the `api` container with production `.env` and mounted storage volumes.
3. Deploy the `worker` container, sharing the database connection and artifact mounts.
4. Deploy the `web` container pointing to the public API URL.
5. Validate `GET /admin/health` on the API.
6. Verify the authentication flow via the Web UI.
7. Confirm the Celery worker is successfully consuming background jobs via Flower.
8. Test end-to-end resume upload and PDF export.
9. Execute a role scrape and verify enrichment data flow.

---

## 📧 OAuth Deployment Notes

If enabling Inbox OTP, public callback URLs are strictly required.

**Standard Callback Patterns:**
- **Google:** `https://api.your-domain.com/inbox/gmail/oauth/callback`
- **Microsoft:** `https://api.your-domain.com/inbox/outlook/oauth/callback`

**Required Provider Scopes:**
- **Gmail:** `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- **Outlook:** `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

*Failure to align these exact scopes and URIs within the Google Cloud Console or Azure AD will result in immediate authentication failures.*

---

## 📋 Post-Deploy Validation Checklist

After every deployment, execute these checks:

1. [ ] Access the landing page and navigate to the dashboard.
2. [ ] Ping `GET /` and `GET /docs` to confirm API availability.
3. [ ] Check `GET /admin/health` ensuring database and Redis are `ok`.
4. [ ] Successfully register a new user or log in.
5. [ ] Upload a test resume and confirm a profile record is created.
6. [ ] Create a target role and manually trigger a scrape.
7. [ ] Ensure jobs populate the feed with `pending` or `completed` enrichment statuses.
8. [ ] Generate a tailored resume and successfully export a PDF.
9. [ ] Initiate a draft or assisted application run; confirm steps/logs are written.
10. [ ] (If enabled) Connect Gmail/Outlook via the Settings page.

---

## 📈 Logging And Operational Checks

Monitor the following operational signals during and after rollout:
- **API:** Review request-scoped structured JSON logs for auth, inbox, or file export anomalies.
- **Worker:** Monitor logs closely for Playwright launch failures or enrichment timeouts.
- **System:** Watch PostgreSQL disk utilization and track the growth of the artifact directory (screenshots and captures can consume significant space over time).
- **Celery:** Utilize the Flower dashboard for queue depth visibility.

---

## 💾 Backup And Recovery

At a minimum, ensure automated backups for:
- The PostgreSQL data directory/volume.
- Uploaded resumes/files located at `STORAGE_PATH`.
- Operational evidence located at `ARTIFACTS_PATH` (if retaining screenshot/run evidence is a requirement).

*Note: If artifact storage is lost but the database survives, the system remains functional, though historical screenshot evidence will return 404s in the UI.*

---

## ⚠️ Known Deployment Gaps

Be aware of the following technical debt items before attempting a massive production scale-out:

1. **Schema Management:** The API relies on `Base.metadata.create_all(...)` on startup. Proper Alembic migrations are required for safe schema evolution.
2. **Compose Constraints:** The checked-in Docker Compose files are heavily skewed toward local development.
3. **Web Server:** The web container currently executes the Next.js development server rather than an optimized production build.
4. **Storage Adapter:** Storage is tightly coupled to the local disk; an S3-compatible adapter is a future requirement.
5. **Database Resets:** Older local development databases may require resets (`docker compose down -v`) due to frequent schema changes during early development.

---

## 🛠️ Recommended Next Hardening Steps

Prioritize these tasks before a formal public launch:

1. Create a dedicated `docker-compose.prod.yml` or Kubernetes manifest.
2. Refactor the `web` container Dockerfile to utilize `next build` and `next start`.
3. Eliminate runtime `create_all` in favor of strict Alembic migrations.
4. Implement an S3-compatible backend for uploads and artifacts.
5. Delegate TLS termination and secret management to external, robust systems (e.g., Traefik/AWS Secrets Manager) rather than relying on `.env` files.