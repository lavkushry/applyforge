# ApplyForge Deployment Guide

This guide outlines the recommended deployment topology, environment configuration, and rollout procedures for running ApplyForge in a production-like environment.

## Deployment Topology

ApplyForge is designed to run as three primary compute services backed by two stateful stores.

### Compute Services
1.  **Web**: Next.js App Router providing the frontend application.
2.  **API**: FastAPI service managing business logic, routing, and database interactions.
3.  **Worker**: Celery worker executing background tasks (e.g., job enrichment, Playwright application automation).

### Stateful Stores
1.  **PostgreSQL**: The primary relational database holding all application state, user data, and analytical records.
2.  **Redis**: Utilized as the message broker for Celery task queuing and orchestration.

### Storage Paths
Both the API and Worker instances require access to persistent file storage paths:
*   `STORAGE_PATH`: Stores user-uploaded resumes and system-generated PDF exports.
*   `ARTIFACTS_PATH`: Stores worker-generated diagnostic evidence, including step screenshots and enrichment snapshots.

*Note: Currently, ApplyForge assumes a local-disk or shared-volume storage topology. Migration to S3-compatible object storage is planned for a future release.*

## Environment Configuration

A successful deployment requires properly configuring environment variables across all services.

### Core Connections
*   `DATABASE_URL`: Connection string for PostgreSQL (e.g., `postgresql://user:pass@host:5432/db`).
*   `REDIS_URL`: Connection string for Redis (e.g., `redis://host:6379/0`).

### API Configuration
*   `SECRET_KEY`: A strong, randomly generated secret used for cryptographic signing (JWTs, session tokens).
*   `FRONTEND_URL`: The publicly accessible URL of the Web service (e.g., `https://app.applyforge.dev`). Used for CORS policies and webhook callbacks.
*   `API_URL`: The publicly accessible URL of the API service (e.g., `https://api.applyforge.dev`).

### Worker Configuration
*   `PLAYWRIGHT_BROWSERS_PATH`: (Optional) Custom path for Playwright browser binaries if not utilizing the default system locations.

### Web Configuration
*   `NEXT_PUBLIC_API_URL`: The publicly accessible URL of the API service, utilized by the frontend for client-side routing.

## Network Routing and Ports

In a typical containerized or clustered environment, ensure the following default ports are correctly routed or exposed:

*   **API**: Port `8000` (HTTP)
*   **Web**: Port `3000` (HTTP)
*   **Flower** (Worker UI): Port `5555` (HTTP)
*   **Redis**: Port `6379` (TCP)
*   **PostgreSQL**: Port `5432` (TCP)

## Recommended Rollout Procedure

Follow this sequence for a safe, structured deployment:

1.  **Provision Stateful Stores**: Deploy and verify connectivity to PostgreSQL and Redis.
2.  **Deploy API**: Deploy the API service configured with the production environment variables and mounted persistent storage volumes.
3.  **Deploy Worker**: Deploy the Celery worker, ensuring it connects to the same PostgreSQL database, Redis broker, and artifact storage paths.
4.  **Deploy Web**: Deploy the Next.js frontend, ensuring `NEXT_PUBLIC_API_URL` points to the successfully deployed API endpoint.
5.  **Verify Health Checks**: Navigate to `[API_URL]/admin/health` to confirm the database and Redis connections are operational.
6.  **Verify Authentication**: Execute a test registration and login flow via the web interface.
7.  **Verify Worker Operations**: Trigger a job scrape or enrichment task and confirm the worker successfully consumes and completes it.
8.  **Verify File Operations**: Upload a test resume and generate an exported PDF.
9.  **Verify Integrations**: If OAuth is configured, test the Gmail/Outlook connection flow.

## OAuth Integration Setup

If your deployment supports Inbox OTP retrieval, configure the OAuth callback URLs appropriately within your provider's developer console.

**Recommended Callback URL Patterns:**
*   Google: `https://api.yourdomain.com/inbox/gmail/oauth/callback`
*   Microsoft: `https://api.yourdomain.com/inbox/outlook/oauth/callback`

**Required Provider Scopes:**
*   **Gmail**: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
*   **Outlook**: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

Ensure the corresponding Client ID and Secret environment variables are set in the API configuration.

## Post-Deploy Validation Checklist

Perform these checks immediately following any deployment:

1.  [ ] Verify the landing page and dashboard load correctly.
2.  [ ] Verify the API root (`GET /`) and documentation (`GET /docs`) are accessible.
3.  [ ] Verify `GET /admin/health` reports `status: ok` for both database and redis.
4.  [ ] Successfully register or log in using a test account.
5.  [ ] Upload a resume and verify the candidate profile is generated.
6.  [ ] Create a target role and manually trigger a scrape run.
7.  [ ] Confirm jobs appear in the feed with `pending` or `completed` enrichment states.
8.  [ ] Execute a tailoring operation and successfully export a PDF resume.
9.  [ ] Initiate a draft application run and verify step logs are recorded.
10. [ ] (Optional) Connect an Inbox provider via the Settings page.

## Observability and Logging

Monitor the following operational signals:

*   **API**: Request-scoped structured logs (monitor for auth, inbox, and file export errors).
*   **Worker**: Playwright launch diagnostics and task enrichment failures (monitor via Flower or container logs).
*   **PostgreSQL**: Monitor disk growth and query performance.
*   **Storage**: Monitor artifact directory growth (screenshots and enrichment captures).

## Backup Strategy

At a minimum, ensure regular, automated backups for:
*   PostgreSQL database contents.
*   Files within the `STORAGE_PATH` (user resumes and generated PDFs).
*   *(Optional but recommended)* Files within the `ARTIFACTS_PATH` if retaining historical run evidence is required.

## Known Limitations and Caveats

Please be aware of the following current system limitations:

1.  **Schema Migrations**: The API currently executes `Base.metadata.create_all(...)` on startup. Schema evolution is not yet fully managed via Alembic migrations.
2.  **Compose Configuration**: The provided `docker-compose.yml` is explicitly tailored for local development and should not be used as-is for production.
3.  **Next.js Server**: The default web container utilizes the Next.js development server (`next dev`). Production deployments must be updated to use `next build` and `next start`.
4.  **Storage Engine**: Storage is currently restricted to local disk or mounted volumes. S3 integration is pending.
