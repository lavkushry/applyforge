# ApplyForge Local Development with Docker

## Overview

This guide provides the most efficient method for running the complete ApplyForge stack locally using Docker.

This approach is ideal if you need:
- The entire application stack (Web frontend, API backend, asynchronous Worker).
- Integrated PostgreSQL and Redis instances.
- To perform manual end-to-end testing without installing Python or Node.js directly on your local machine.

## Bootstrapped Services

Running the provided [docker-compose.yml](../infra/docker-compose.yml) will initialize the following services:

- `db` (PostgreSQL) mapped to port `5432`
- `redis` mapped to port `6379`
- `api` (FastAPI) mapped to port `8000`
- `web` (Next.js) mapped to port `3000`
- `flower` (Celery Monitoring) mapped to port `5555`
- `worker` (Celery Worker) running in the background

## Local Environment Caveats

The current Docker Compose configuration is heavily optimized for development:

- Source code directories are actively mounted into the running containers.
- Environment variables are sourced primarily from the provided example `.env` files, supplemented by local overrides if present.
- The Next.js `web` container executes in development mode using the dev server.
- The `api` container automatically attempts to create database tables upon startup.

*Warning: This setup is designed for rapid iteration and testing. It lacks the security hardening and optimizations required for a production deployment.*

## System Prerequisites

Ensure you have the following installed on your host machine:
- Docker
- Docker Compose

Verify your installations with:

```bash
docker --version
docker compose version
```

## Method 1: Rapid Startup (Using Example Configurations)

This method utilizes the pre-committed `.env.example` files without modification.

```bash
cd ../infra
docker compose up --build
```

Once initialized, access the services via your browser:

- Web Application: `http://localhost:3000`
- API Documentation: `http://localhost:8000/docs`
- Flower Dashboard: `http://localhost:5555`

This is the fastest way to verify the stack locally.

If accessing these services from another device on your local network, substitute `localhost` with the host machine's IP address (e.g., `172.24.28.220`).

*Important Note regarding Redis:* Port `6379` serves the Redis protocol, not HTTP traffic. The correct connection string is `redis://172.24.28.220:6379/0`, not an `http://` URL.

## Method 2: Startup with Custom Environment Variables

To inject actual secrets or OAuth credentials, generate local environment files based on the examples:

```bash
cp ../apps/api/.env.example ../apps/api/.env
cp ../apps/web/.env.example ../apps/web/.env.local
cp ../apps/worker/.env.example ../apps/worker/.env
cp ../infra/.env.example ../infra/.env
```

Next, configure the host IP within `../infra/.env`:

```bash
PUBLIC_HOST=172.24.28.220
```

Then launch the stack:

```bash
cd ../infra
docker compose up --build
```

By defining `PUBLIC_HOST`, the publicly accessible URLs will update accordingly (e.g., `http://172.24.28.220:3000`). Internal container communication will continue to utilize Docker's internal DNS (e.g., `db:5432`).

## Populating Test Data

After the services have successfully started, execute the database seed script from a new terminal session:

```bash
cd ../infra
docker compose exec api python -m app.db.seed
```

You can then log in using the bootstrapped credentials:
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

*Note: This default account is exclusively provisioned during local Docker Compose seeding and is disabled in other deployment scenarios.*

## Validating the Installation

Execute the following checks to confirm the stack is operating correctly:

### API Root Verification

```bash
curl http://localhost:8000/
```
Expected response: `{"name": "ApplyForge API", "status": "running"}`

### Health Status Endpoint

```bash
curl http://localhost:8000/admin/health
```
Expected response fields: `status: ok`, `database: ok`, `redis: ok`

### Browser Checks

- Verify the Web UI at `http://localhost:3000`
- Verify the Worker status via Flower at `http://localhost:5555`

## Helpful Docker Commands

Run services in detached mode (background):
```bash
cd ../infra
docker compose up --build -d
```

Stream live logs:
```bash
cd ../infra
docker compose logs -f api worker web
```

Halt all services:
```bash
cd ../infra
docker compose down
```

Halt services and permanently wipe database volumes:
```bash
cd ../infra
docker compose down -v
```

## Typical Local Testing Scenario

1. Seed the database with demo data.
2. Authenticate via the Web UI.
3. Navigate to `/wizard` to check system readiness.
4. Upload a sample resume.
5. Define a target role and initiate a background scrape.
6. Verify that new jobs populate the feed.
7. Generate a tailored resume and export it as a PDF.
8. Trigger a draft or assisted application process.
9. Inspect `/admin` and `/runs/[id]` to review execution logs and captured screenshots.

## Configuring Local OAuth

To test Gmail or Outlook integrations locally, your `api/.env` file must contain valid OAuth credentials.

Set your provider's app registration to use these exact callback URLs:
- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

## Troubleshooting Common Issues

### Port Conflicts
If a required port (e.g., `3000`, `5432`) is occupied, terminate the conflicting application or alter the port mappings within [docker-compose.yml](../infra/docker-compose.yml).

### Inactive Worker
If tasks are queuing but not processing, inspect the worker and redis logs:
```bash
cd ../infra
docker compose logs -f worker redis
```

### Database Schema Mismatches
Because the API attempts to create tables on startup, an existing local database might conflict with newly added columns. To resolve this, perform a clean reset:
```bash
cd ../infra
docker compose down -v
docker compose up --build
```
Remember to re-run the seed script afterward.

### Missing OAuth Options
If the UI indicates OAuth providers are unconfigured, ensure the following variables are correctly defined in your API environment:
- `GOOGLE_OAUTH_CLIENT_ID` / `SECRET`
- `MICROSOFT_OAUTH_CLIENT_ID` / `SECRET`

## Further Reading

- [Deployment Guide](../docs/DEPLOYMENT.md)
- [System Architecture](../docs/ARCHITECTURE.md)
- [Main README](../README.md)
