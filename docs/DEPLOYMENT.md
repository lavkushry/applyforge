# ApplyForge Deployment Documentation

This guide outlines the recommended strategies and prerequisites for running ApplyForge across different environments.

## Deployment Strategies

ApplyForge is designed to run in two primary configurations:

1. **Local/Staging (Docker Compose)**: Ideal for testing, continuous integration, or local operations.
2. **Production Single-VM**: A hardened setup utilizing Docker containers behind a reverse proxy on a dedicated Linux host.

*Note on current Compose defaults*: The default `docker-compose.yml` included in `infra/` is optimized for active development. It mounts local directories, utilizes `.env.example` placeholders, and runs Next.js in development mode. For staging or production, you must override these defaults.

## Architectural Components

A complete ApplyForge deployment consists of five services:

- **Web Frontend**: Next.js (Port `3000`)
- **API Backend**: FastAPI (Port `8000`)
- **Task Worker**: Celery executing Playwright
- **Database**: PostgreSQL 16
- **Cache & Broker**: Redis 7
- *(Optional)* **Monitoring**: Flower dashboard (Port `5555`)

## Environment Variable Configuration

Before launching any environment, proper secrets must be defined.

### Configuring the API

Copy the example file: `cp apps/api/.env.example apps/api/.env`

Required modifications for production:
- `ENV=prod`
- `WEB_ORIGIN=https://your-frontend-domain.com`
- `DATABASE_URL` (Point to your persistent Postgres instance)
- `REDIS_URL` (Point to your Redis instance)
- `SECRET_KEY` (Generate a cryptographically secure random string)
- `ACCESS_COOKIE_SECURE=true` (Required for HTTPS environments)
- `OPENAI_API_KEY` (Valid API key for LLM operations)

**Optional OAuth Settings (for Inbox OTPs):**
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID` / `MICROSOFT_OAUTH_CLIENT_SECRET` / `MICROSOFT_OAUTH_TENANT` / `MICROSOFT_OAUTH_REDIRECT_URI`

### Configuring the Web Application

Copy the example file: `cp apps/web/.env.example apps/web/.env.local`

Required modifications:
- `NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com`

### Configuring the Worker

Copy the example file: `cp apps/worker/.env.example apps/worker/.env`

Required modifications:
- `DATABASE_URL` and `REDIS_URL` (Must match API settings)
- `ARTIFACTS_PATH=/path/to/persistent/storage`
- `PLAYWRIGHT_HEADLESS=true`

## Staging Deployment via Docker Compose

### 1. Initialize Environments
Ensure all `.env` files are populated with staging-appropriate values.

### 2. Override the Compose File
The default `infra/docker-compose.yml` hardcodes paths to `.env.example` files. You must modify the `env_file` directives to target your real `.env` files, or use a `docker-compose.override.yml`.

### 3. Launch Services
```bash
cd infra
docker compose up --build -d
```

### 4. Verify Health
Check the primary entry points:
- Frontend: `http://localhost:3000`
- API Health Endpoint: `http://localhost:8000/admin/health` (Should return `status=ok`, `database=ok`, `redis=ok`)

## Production Deployment (Single VM)

For a single-node production deployment, place all containers behind an SSL-terminated reverse proxy (e.g., Nginx, Caddy, or Traefik).

### Volume Management

The API and Worker require durable, persistent storage on the host machine:
- PostgreSQL Data Directory
- User Uploads (`STORAGE_PATH`)
- Application Artifacts / Screenshots (`ARTIFACTS_PATH`)

Example host mappings:
- `/srv/applyforge/postgres`
- `/srv/applyforge/uploads`
- `/srv/applyforge/artifacts`

### Reverse Proxy Configuration

Route traffic securely to internal container ports:
- `https://app.example.com` routes to the Web container (Internal `3000`)
- `https://api.example.com` routes to the API container (Internal `8000`)

**Crucial Cross-Origin (CORS) Rules:**
- Ensure `WEB_ORIGIN` in the API strictly matches `https://app.example.com`.
- Ensure `NEXT_PUBLIC_API_BASE_URL` in the frontend strictly matches `https://api.example.com`.
- Set `ACCESS_COOKIE_SECURE=true`.

### OAuth Provider Setup

If enabling Inbox integrations, exact URI matching is mandatory on the provider side.
- Google Callback: `https://api.example.com/inbox/gmail/oauth/callback`
- Microsoft Callback: `https://api.example.com/inbox/outlook/oauth/callback`

Required Provider Scopes:
- **Google**: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- **Microsoft**: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

## Rollout Validation Sequence

Upon completing a deployment, manually verify these core flows:

1. Assess `/admin/health` on the API.
2. Complete a new user registration and login.
3. Upload a sample resume and confirm text extraction completes.
4. Define a target role and initiate a discovery scrape.
5. Verify jobs populate the feed and complete enrichment.
6. Trigger a PDF export of a tailored resume.
7. Launch a Draft application run and confirm steps log successfully.
8. (If configured) Connect a Gmail or Outlook account via Settings.

## Monitoring and Maintenance

### Key Observability Metrics
- Monitor API logs for unexpected auth rejections or PDF export crashes.
- Monitor Worker logs for Playwright timeouts or enrichment blocking.
- Track storage volume growth, particularly `ARTIFACTS_PATH`, as screenshots accumulate rapidly.

### Backups
To fully restore the platform, you must back up:
- The PostgreSQL database dump.
- The `STORAGE_PATH` contents (contains user resumes).
- *Optional*: `ARTIFACTS_PATH` (contains historical run screenshots).

## Known Production Hurdles

Before migrating to a public release, be aware of these architectural caveats:
1. The API utilizes `Base.metadata.create_all()` on boot. Full Alembic migration management is pending.
2. The bundled `docker-compose.yml` runs `next dev`. It must be altered to execute `next build && next start` for production performance.
3. File storage is purely local. S3-bucket integrations are not yet implemented natively.

Prioritize addressing the Next.js build process and migrating to Alembic scripts before onboarding external users.