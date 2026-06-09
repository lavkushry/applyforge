# ApplyForge Production and Staging Deployment

## Deployment Architecture

ApplyForge is currently structured to support two primary deployment models:

1. A local or staging environment managed via Docker Compose.
2. A single-virtual-machine production setup utilizing the same containerized service architecture.

While the `infra/` directory provides functional container configurations, the included `docker-compose.yml` is fundamentally tailored for local development. Specifically, it relies on live source code mounting, uses generic example environment files, runs the Next.js frontend in development mode, and allows the API to automatically generate database tables upon launch. Therefore, this Compose file requires significant overrides before being considered production-ready.

## Service Topology

The complete ApplyForge stack consists of the following core services:

- `web`: The Next.js frontend application (default port `3000`).
- `api`: The FastAPI backend service (default port `8000`).
- `worker`: The Celery task executor responsible for job enrichment and automated applications.
- `db`: The primary PostgreSQL 16 database.
- `redis`: The Redis 7 instance serving as both the Celery message broker and application cache.

An additional, optional service is also available:
- `flower`: A web-based dashboard for monitoring Celery tasks (default port `5555`).

## Environment Variable Configuration

Before deploying, you must create and populate the necessary environment files.

### API Configuration

Begin by copying the template: [apps/api/.env.example](../apps/api/.env.example).

Crucial variables to update for production:
- `ENV`: Set to `prod`.
- `WEB_ORIGIN`: Ensure this matches your frontend domain (e.g., `https://your-web-domain.com`).
- `DATABASE_URL`: Provide the full PostgreSQL connection string.
- `REDIS_URL`: Provide the full Redis connection string.
- `SECRET_KEY`: Generate a robust, cryptographically secure random string.
- `ACCESS_COOKIE_SECURE`: Must be `true` for environments served over HTTPS.
- `OPENAI_API_KEY`: Insert your active OpenAI API key.

To enable Inbox OTP integrations, also define:
- `GOOGLE_OAUTH_CLIENT_ID` / `SECRET` / `REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID` / `SECRET` / `TENANT` / `REDIRECT_URI`

### Web Configuration

Begin by copying the template: [apps/web/.env.example](../apps/web/.env.example).

Required updates:
- `NEXT_PUBLIC_API_BASE_URL`: Point this to your publicly accessible API domain (e.g., `https://api.your-domain.com`).

### Worker Configuration

Begin by copying the template: [apps/worker/.env.example](../apps/worker/.env.example).

Required updates:
- `DATABASE_URL` and `REDIS_URL`: These must match the backend API's connection strings.
- `ARTIFACTS_PATH`: Specify the absolute path for persistent artifact storage.
- `PLAYWRIGHT_HEADLESS`: Ensure this remains `true` for server environments.

## Staging Deployment via Docker Compose

### 1. File Preparation
Generate the required environment files as outlined above:
```bash
cp ../apps/api/.env.example ../apps/api/.env
cp ../apps/web/.env.example ../apps/web/.env.local
cp ../apps/worker/.env.example ../apps/worker/.env
```

### 2. Compose File Adjustments
The default `docker-compose.yml` hardcodes paths to the `.env.example` files. You must either edit these `env_file` directives to point to your newly created actual `.env` files or utilize a `docker-compose.override.yml` to inject the correct paths.

### 3. Execution
Launch the application stack:
```bash
cd ../infra
docker compose up --build
```

### 4. Verification
Ensure the following endpoints are accessible:
- Web App: `http://localhost:3000`
- API Root: `http://localhost:8000/`
- API Documentation: `http://localhost:8000/docs`
- System Health: `http://localhost:8000/admin/health` (Should return `{status: ok, database: ok, redis: ok}`)
- Flower Monitor: `http://localhost:5555`

## Single-Node Production Deployment

For a robust single-server deployment, the recommended setup involves containerizing the services and placing them behind a reverse proxy.

### Infrastructure Layout
- **Reverse Proxy:** Nginx, Traefik, or Caddy managing ingress.
- **Containers:** `web`, `api`, `worker`, `db`, and `redis`.
- **Persistent Storage:** Docker volumes mapped to host directories for PostgreSQL data, user uploads, and worker artifacts.

### Storage Mounts
To prevent data loss, ensure the following host paths are mounted to the respective containers:
- Database: `/srv/applyforge/postgres`
- Uploads (`STORAGE_PATH`): `/srv/applyforge/uploads`
- Artifacts (`ARTIFACTS_PATH`): `/srv/applyforge/artifacts`

### Routing & CORS Configuration
A typical routing strategy separates the frontend and backend:
- `https://app.example.com` routing to the `web` container.
- `https://api.example.com` routing to the `api` container.

It is critical that the `WEB_ORIGIN` variable in the API environment exactly matches the public URL of the web frontend. The API relies on this variable to configure its CORS policy, and a mismatch will cause authentication and API requests to fail.
Similarly, ensure that the OAuth redirect URIs align perfectly with the public API URL.

## Managing OAuth Integrations

If you intend to utilize the inbox OTP functionality, precise configuration of OAuth callback URLs is mandatory.

Standard callback structures:
- Google: `https://api.example.com/inbox/gmail/oauth/callback`
- Microsoft: `https://api.example.com/inbox/outlook/oauth/callback`

Ensure your application registrations with Google and Microsoft request the exact scopes expected by ApplyForge; otherwise, the connection process will fail.

## Post-Deployment Validation

Always perform a comprehensive functional test after any deployment:

1. Navigate to the public web application and dashboard.
2. Confirm the API is reachable at its root and `/docs` endpoints.
3. Validate backend connections via the `/admin/health` endpoint.
4. Successfully execute a user registration and login flow.
5. Upload a resume to verify file storage and profile creation.
6. Configure a target role and initiate a background job scrape.
7. Verify jobs appear in the feed and successfully transition through the enrichment process.
8. Trigger a tailored resume generation and download the resulting PDF.
9. Launch a test application run (draft or assisted) and ensure the execution steps are logged.
10. If configured, authenticate an inbox connection via the settings page.

## System Monitoring

Monitor the following indicators to maintain system health:
- Request-scoped structured logs generated by the API.
- The `/admin/health` endpoint and internal diagnostics dashboard.
- The Flower UI for Celery task queuing and execution status.
- Disk usage metrics, particularly regarding PostgreSQL data growth and the accumulation of worker screenshots in the artifacts directory.

## Backup Strategy

At a minimum, implement regular backups for:
- The PostgreSQL database volume.
- The user upload directory (`STORAGE_PATH`).
- The worker artifacts directory (`ARTIFACTS_PATH`), to preserve historical application evidence.

## Current Production Limitations

Be aware of the following architectural gaps before deploying to a high-stakes environment:

1. The FastAPI backend still relies on `Base.metadata.create_all(...)` during startup rather than a strict Alembic migration flow.
2. The provided `docker-compose.yml` requires modification to be secure and performant in production.
3. The `web` container runs the Next.js dev server (`npm run dev`); this must be changed to `npm run build` and `npm start`.
4. File storage currently relies entirely on local disk mounts; integration with S3-compatible object storage is pending.
5. If migrating an older local development database, schema conflicts may require a manual reset due to structural changes during the MVP phase.
