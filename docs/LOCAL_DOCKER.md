# ApplyForge Local Docker Setup Guide

## Purpose

This guide provides the fastest methodology for running ApplyForge locally utilizing Docker.

**Utilize this approach if you require:**
- The complete Web + API + Worker stack.
- Built-in PostgreSQL and Redis instances.
- Immediate local manual testing capabilities without installing Python and Node on your host machine.

## Provided Services

The included `infra/docker-compose.yml` initiates the following services:
- **`db`**: PostgreSQL on port `5432`.
- **`redis`**: Redis on port `6379`.
- **`api`**: FastAPI backend on port `8000`.
- **`web`**: Next.js frontend on port `3000`.
- **`flower`**: Celery dashboard on port `5555`.
- **`worker`**: Celery worker operating as a background service.

## Important Local Behaviors

The provided Compose file is strictly optimized for development workflows:
- The local source tree is mounted directly into the containers.
- It prioritizes reading `.env.example` files, falling back to local `.env` files if present.
- The web container purposefully runs the Next.js development server.
- The API explicitly drops and recreates database tables upon startup.

*Note: While acceptable for local testing, this configuration is unequivocally unsuited for hardened production deployments.*

## Prerequisites

- Docker installed and running.
- Docker Compose plugin.

Verify your installation:
```bash
docker --version
docker compose version
```

## Option 1: Fastest Local Startup

This method directly utilizes the provided example environment files without modification.

```bash
cd infra
docker compose up --build
```

**Access Points:**
- Web Interface: `http://localhost:3000`
- API Documentation: `http://localhost:8000/docs`
- Flower Dashboard: `http://localhost:5555`

If accessing the stack from an external machine on the same network, replace `localhost` with the Docker host's IP address (e.g., `172.24.28.220`):
- Web: `http://172.24.28.220:3000`
- API Docs: `http://172.24.28.220:8000/docs`
- Flower: `http://172.24.28.220:5555`

**Crucial Note Regarding Redis:**
Port `6379` is exclusively for Redis, which is not an HTTP service. The correct connection string is `redis://172.24.28.220:6379/0`, not an `http://` URL.

## Option 2: Startup With Custom Environment Variables

To utilize real secrets or actual OAuth credentials, you must construct local environment files:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
cp infra/.env.example infra/.env
```

Next, define your host IP within `infra/.env`:
```bash
PUBLIC_HOST=172.24.28.220
```

Initiate the stack:
```bash
cd infra
docker compose up --build
```

With `PUBLIC_HOST=172.24.28.220` established, external access behaves identically to Option 1, while internal Docker traffic continues utilizing service names (e.g., `db:5432`, `redis:6379`).

## Seeding Demo Data

Once the stack is operational, open a new terminal session to seed demonstration data:

```bash
cd infra
docker compose exec api python -m app.db.seed
```

**First Local Login Credentials:**
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

*Note: This bootstrap account is exclusively enabled via local Docker Compose setups and remains disabled by default in generic non-production environments.*

## Smoke Checks

Execute these verifications post-startup:

### API Root
```bash
curl http://localhost:8000/
```
*Expected Output:* `{"name": "ApplyForge API", "status": "running"}`

### Health Endpoint
```bash
curl http://localhost:8000/admin/health
```
*Expected Output:* `{"status": "ok", "database": "ok", "redis": "ok"}`

### Web & Worker Visibility
- Open `http://localhost:3000` in a browser to confirm the frontend renders.
- Open `http://localhost:5555` in a browser; Flower should display the active Celery worker.

*(Replace `localhost` with your host IP if testing externally).*

## Useful Local Commands

**Start Detached (Background):**
```bash
cd infra
docker compose up --build -d
```

**Follow Logs:**
```bash
cd infra
docker compose logs -f api worker web
```

**Stop Stack:**
```bash
cd infra
docker compose down
```

**Stop Stack & Destroy Volumes (Resets Local DB):**
```bash
cd infra
docker compose down -v
```

## Common Local Testing Workflow

1. Seed the demo data.
2. Authenticate via the web application.
3. Navigate to `/wizard` and verify readiness.
4. Upload a test resume.
5. Define a role and execute a scrape.
6. Verify jobs populate correctly.
7. Tailor a resume and export the PDF.
8. Initiate a draft or assisted application run.
9. Inspect `/admin` and `/runs/[id]` to view logs and screenshots.

## Local OAuth Configuration

For local Gmail or Outlook integrations to function, the API environment must contain valid OAuth credentials.

**Recommended Local Callback URIs:**
- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

*The provider application registration must explicitly match these URIs.*

## Troubleshooting

### Port Conflicts
If ports `3000`, `5432`, `6379`, `8000`, or `5555` are already bound, terminate the conflicting host processes or adjust the published port mappings within `docker-compose.yml`.

### Worker Inactivity
Inspect worker and Redis logs:
```bash
cd infra
docker compose logs -f worker redis
```

### Inconsistent Database Schema
Because the API aggressively creates tables at startup, older local databases may severely conflict with newly introduced columns.

To rectify, perform a destructive reset:
```bash
cd infra
docker compose down -v
docker compose up --build
```
Then, re-seed the data.

### OAuth UI indicates "Provider Not Configured"
Verify your `apps/api/.env` file correctly defines:
- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`
- *or*
- `MICROSOFT_OAUTH_CLIENT_ID` and `MICROSOFT_OAUTH_CLIENT_SECRET`

## Related Documentation

- `docs/DEPLOYMENT.md`
- `docs/ARCHITECTURE.md`
- `README.md`
