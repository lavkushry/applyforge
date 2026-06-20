<!-- REWRITTEN DOCUMENT: DEPLOYMENT.md -->
<!-- This document has been comprehensively reviewed and rewritten for clarity and consistency. -->

# ApplyForge Deployment Guide

## Section: Deployment Posture

ApplyForge currently supports two practical deployment modes:

1. local or staging deployment with Docker Compose
2. a single-VM production-style deployment with the same service split

The repository already includes runnable container definitions under `infra/`, but the current compose file is development-oriented:

- it mounts source code into containers
- it uses the example env files directly
- the web container runs `npm run dev`
- the API still creates tables at startup with `Base.metadata.create_all(...)`

That means Compose is a good staging and operator test path today, but it should not be treated as a hardened production artifact without overrides.

## Section: Runtime Components

ApplyForge has five runtime services:

- `web`: Next.js frontend on port `3000`
- `api`: FastAPI service on port `8000`
- `worker`: Celery worker for enrichment and application execution
- `db`: PostgreSQL 16
- `redis`: Redis 7 for Celery broker and cache

Optional:

- `flower`: Celery dashboard on port `5555`

## Section: Required Environment Files

Create real env files before deployment.

### API

Begin by using [apps/api/.env.example](../apps/api/.env.example).

Minimum values to change:

- `ENV=prod`
- `WEB_ORIGIN=https://your-web-domain`
- `DATABASE_URL=postgresql+psycopg2://...`
- `REDIS_URL=redis://...`
- `SECRET_KEY=<strong-random-secret>`
- `ACCESS_COOKIE_SECURE=true`
- `OPENAI_API_KEY=<real-key>`

If inbox OTP is enabled, also set:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

### Web

Begin by using [apps/web/.env.example](../apps/web/.env.example).

Set:

- `NEXT_PUBLIC_API_BASE_URL=https://your-api-domain`

### Worker

Begin by using [apps/worker/.env.example](../apps/worker/.env.example).

Set:

- `DATABASE_URL=postgresql+psycopg2://...`
- `REDIS_URL=redis://...`
- `ARTIFACTS_PATH=/data/artifacts`
- `PLAYWRIGHT_HEADLESS=true`

## Section: Local Or Staging Deployment With Compose

### 1. Prepare env files

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

Fill in real values.

### 2. Important compose limitation

The checked-in [docker-compose.yml](../infra/docker-compose.yml) references the example env files:

- `../apps/api/.env.example`
- `../apps/web/.env.example`
- `../apps/worker/.env.example`

Before using Compose outside a demo setup, update those `env_file` entries to point at your real env files, or create a compose override that does so.

### 3. Start the stack

```bash
cd infra
docker compose up --build
```

### 4. Smoke checks

After the stack is up:

- web: `http://localhost:3000`
- API root: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`
- health: `http://localhost:8000/admin/health`
- Flower: `http://localhost:5555`

Expected health shape:

- `status=ok`
- `database=ok`
- `redis=ok`

## Section: Single-VM Production-Style Deployment

Use this when you want one Linux host with Docker and a reverse proxy.

### Recommended layout

- reverse proxy: Nginx, Caddy, or Traefik
- `web`, `api`, `worker`, `db`, `redis` as containers
- persistent volumes for PostgreSQL, uploads, and artifacts

### Required persistent paths

The API and worker write to local storage today.

- API upload storage: `STORAGE_PATH`
- API artifact storage: `ARTIFACTS_PATH`
- worker artifact storage: `ARTIFACTS_PATH`

Recommended host mounts:

- `/srv/applyforge/postgres`
- `/srv/applyforge/uploads`
- `/srv/applyforge/artifacts`

### Reverse proxy routing

Recommended public routing:

- `https://app.example.com` → web container
- `https://api.example.com` → API container

If you keep both behind one domain, make sure:

- `WEB_ORIGIN` matches the web origin exactly
- `NEXT_PUBLIC_API_BASE_URL` points at the reachable API base URL
- OAuth redirect URIs use the final public API callback URLs

### Cookie and CORS settings

For HTTPS deployment:

- set `ACCESS_COOKIE_SECURE=true`
- set `WEB_ORIGIN` to the exact public web origin

The API currently derives CORS from `WEB_ORIGIN`, so a mismatch here will break auth and browser API calls.

Port reminder:

- API is HTTP on `8000`
- web is HTTP on `3000`
- Flower is HTTP on `5555`
- Redis uses `redis://...:6379/0`

For example, on a host with IP `172.24.28.220`:

- web: `http://172.24.28.220:3000`
- API: `http://172.24.28.220:8000`
- Flower: `http://172.24.28.220:5555`
- Redis: `redis://172.24.28.220:6379/0`

### Example rollout order

1. provision PostgreSQL and Redis
2. deploy API with real env and mounted storage
3. deploy worker with shared DB and artifact config
4. deploy web with the public API URL
5. verify `/admin/health`
6. verify login flow
7. verify worker is consuming jobs
8. verify file upload and resume export
9. verify role scrape and enrichment

## Section: OAuth Deployment Notes

Inbox OTP support depends on public callback URLs.

Recommended callback patterns:

- Google: `https://api.example.com/inbox/gmail/oauth/callback`
- Microsoft: `https://api.example.com/inbox/outlook/oauth/callback`

Provider scopes currently expected by the app:

- Gmail: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- Outlook: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

If these values do not match the provider app registration, inbox connect will fail even if the rest of the deployment is healthy.

## Section: Post-Deploy Validation Checklist

Run these checks after each deployment:

1. Open the landing page and dashboard.
2. Open `GET /` and `GET /docs` on the API host and confirm the API is reachable.
3. Hit `GET /admin/health` and confirm database and Redis are both `ok`.
4. Register or log in through the web app.
5. Upload a resume and confirm a profile record is created.
6. Create a target role and run a scrape.
7. Confirm jobs appear with `pending` or `completed` enrichment state.
8. Trigger tailoring and export a resume PDF.
9. Start a draft or assisted application run and confirm steps are written.
10. If OAuth is configured, connect Gmail or Outlook from Settings.

## Section: Logging And Operational Checks

Current operational signals:

- API request-scoped structured logs
- `/admin/health`
- run diagnostics in `/admin`
- retry metadata on application runs
- Flower for Celery visibility

Things to watch during rollout:

- API logs for auth, inbox, and file export failures
- worker logs for Playwright launch issues or enrichment failures
- PostgreSQL disk growth
- artifact directory growth from screenshots and enrichment captures

## Section: Backup And Recovery

At minimum, back up:

- PostgreSQL data
- uploaded resumes and exported files under `STORAGE_PATH`
- artifacts under `ARTIFACTS_PATH` if you want run evidence and screenshots retained

If you lose artifact storage but keep PostgreSQL, the product will still have run records but screenshot and export evidence may be missing.

## Section: Known Deployment Gaps

These are real current limitations, not hypothetical ones:

1. The API still runs `Base.metadata.create_all(...)` at startup in [main.py](../apps/api/app/main.py), so schema evolution is not yet fully migration-driven.
2. The checked-in Compose setup is development-oriented and should be overridden for production use.
3. The web container currently runs the Next.js dev server rather than a production build server.
4. Storage is local-disk based today; S3-compatible object storage is still future work.
5. Existing older local databases may need a reset or migration because the schema has changed repeatedly during development.

## Section: Recommended Next Deployment Hardening Steps

Before a real public launch, prioritize:

1. add an explicit production compose or deployment manifest
2. switch the web container to a production `next build` and `next start` flow
3. replace runtime `create_all` with authored Alembic migrations
4. move uploads and artifacts to durable object storage
5. add TLS-terminated public deployment and secret management outside repo-local env files
