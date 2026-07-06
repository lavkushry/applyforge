# ApplyForge Local Environment via Docker

## Overview
This document outlines the most efficient method for running the complete ApplyForge stack locally using Docker. It is ideal for testing the Web, API, and Worker components alongside PostgreSQL and Redis without requiring host-level dependencies.

## Services Included
The default [docker-compose.yml](../infra/docker-compose.yml) provisions:
- `db` (PostgreSQL) on port `5432`
- `redis` on port `6379`
- `api` (FastAPI) on port `8000`
- `web` (Next.js) on port `3000`
- `flower` (Celery Dashboard) on port `5555`
- `worker` (Celery background service)

## Development Configuration Notes
The current setup is heavily optimized for local development:
- Source code directories are mounted as volumes.
- Example environment files are loaded by default, with overrides allowed.
- The web service uses the Next.js development server (`npm run dev`).
- The API auto-generates database tables on startup.
*(Note: This configuration is inherently insecure and unoptimized for production use).*

## System Requirements
Ensure Docker and Docker Compose are installed and running:
```bash
docker --version
docker compose version
```

## Quickstart: Zero-Configuration Launch
To boot the stack using the default example variables:
```bash
cd infra
docker compose up --build
```
Access the services:
- Application: `http://localhost:3000`
- API Swagger: `http://localhost:8000/docs`
- Task Dashboard: `http://localhost:5555`

*(If accessing from a different machine on the local network, substitute `localhost` with the host's IP address. Note that Redis operates on port `6379` via the `redis://` protocol, not HTTP).*

## Customizing Environment Variables
For advanced testing (e.g., OAuth integration), initialize your own environment files:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
cp infra/.env.example infra/.env
```
Update `PUBLIC_HOST` in `infra/.env` if binding to a specific network interface (e.g., `PUBLIC_HOST=192.168.1.100`).

Start the stack normally:
```bash
cd infra
docker compose up --build
```

## Database Seeding
Populate the database with initial testing data by running:
```bash
cd infra
docker compose exec api python -m app.db.seed
```
Default login:
- **Email:** `defaultuser@applyforge.dev`
- **Password:** `defaultuser123`
*(This account is strictly limited to local development environments).*

## Health Verification
Confirm system stability by testing these endpoints:
- **API Base:** `curl http://localhost:8000/` (Should return `{"name": "ApplyForge API", "status": "running"}`)
- **API Health:** `curl http://localhost:8000/admin/health` (Should return `ok` for status, database, and redis)
- **Web UI:** Navigate to `http://localhost:3000`
- **Worker Status:** Navigate to `http://localhost:5555`

## Essential Docker Commands
- **Run detached:** `docker compose up --build -d`
- **View live logs:** `docker compose logs -f api worker web`
- **Shutdown gracefully:** `docker compose down`
- **Nuclear reset (deletes DB volumes):** `docker compose down -v`

## Typical Testing Workflow
1. Seed the database.
2. Authenticate via the Web UI.
3. Complete the onboarding wizard at `/wizard`.
4. Upload a sample resume.
5. Define a target role and trigger discovery.
6. Verify job population.
7. Generate a tailored resume PDF.
8. Initiate a draft application run.
9. Inspect screenshots and logs in the Admin portal (`/runs/[id]`).

## Local OAuth Configuration
To test Gmail or Outlook connectivity, your `apps/api/.env` must contain valid client credentials.
Ensure your OAuth provider is configured with these exact callback URIs:
- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

## Common Issues
- **Port Conflicts:** If ports (3000, 5432, 6379, 8000, 5555) are bound, terminate the offending processes or modify [docker-compose.yml](../infra/docker-compose.yml).
- **Worker Stalling:** Check worker logs via `docker compose logs -f worker redis`.
- **Schema Mismatches:** If API startup fails due to table conflicts, run `docker compose down -v` to reset the database, then rebuild and reseed.
- **OAuth Failures:** Verify `CLIENT_ID` and `CLIENT_SECRET` variables are present and correct in the API environment.

## Further Reading
- [Deployment Guide](DEPLOYMENT.md)
- [Architecture Reference](ARCHITECTURE.md)
- [Main README](../README.md)
