# ApplyForge Local Docker Setup

## Purpose

This guide provides the fastest method for running ApplyForge locally using Docker.

It is intended for developers and operators who need to spin up the complete technology stack (Web, API, Worker, PostgreSQL, and Redis) for local, manual testing without installing Python or Node.js dependencies directly on their host machine.

## Provided Services

The included `infra/docker-compose.yml` configuration starts the following services:

- **`db`**: PostgreSQL Database (Port `5432`)
- **`redis`**: Redis Cache and Message Broker (Port `6379`)
- **`api`**: FastAPI Backend (Port `8000`)
- **`web`**: Next.js Frontend (Port `3000`)
- **`flower`**: Celery Monitoring Dashboard (Port `5555`)
- **`worker`**: Background Celery Executor

## Important Local Development Caveats

The current Docker Compose configuration is specifically tailored for **development**:

- The source code tree is mounted directly into the containers.
- It prioritizes `.env.example` files, falling back to local `.env` files if they are present.
- The `web` container executes the Next.js development server (`next dev`).
- The `api` container dynamically creates database tables on startup using SQLAlchemy's `create_all`.

*Note: While highly convenient for local testing, this configuration is not suitable for a hardened production deployment. For production guidance, see `docs/DEPLOYMENT.md`.*

## Prerequisites

Ensure the following tools are installed and running on your host machine:

- Docker
- Docker Compose

**Verification:**
```bash
docker --version
docker compose version
```

---

## Option 1: Fast Startup (Using Default Examples)

This is the quickest path to launching the application, utilizing the checked-in `.env.example` files without modification.

```bash
cd infra
docker compose up --build
```

**Access Points (Localhost):**
- Web App: `http://localhost:3000`
- API Documentation: `http://localhost:8000/docs`
- Flower Dashboard: `http://localhost:5555`

**Access Points (Network):**
If you are accessing the stack from another machine on the same local network, replace `localhost` with the Docker host's IP address (e.g., `172.24.28.220`).

*Important Note regarding Redis: Port `6379` is the Redis protocol port. It is not an HTTP service. The correct internal connection string is `redis://172.24.28.220:6379/0`.*

---

## Option 2: Startup with Custom Environment Values

If you need to test with real secrets, API keys, or OAuth credentials, you must establish local `.env` files first.

### 1. Copy Environment Files

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
cp infra/.env.example infra/.env
```

### 2. Configure Host IP (Optional)

If accessing across a network, set the `PUBLIC_HOST` in `infra/.env`:

```bash
PUBLIC_HOST=172.24.28.220
```

### 3. Launch Stack

```bash
cd infra
docker compose up --build
```

*(Browser URLs will now utilize the configured `PUBLIC_HOST` instead of `localhost`.)*

---

## Seeding Demo Data

Once the stack is fully operational, you can seed the database with initial demo data. Open a separate terminal window and execute:

```bash
cd infra
docker compose exec api python -m app.db.seed
```

**Initial Local Login Credentials:**
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

*(Note: This bootstrap account is exclusively enabled within the local Docker Compose environment and is disabled in production setups.)*

---

## Post-Startup Smoke Checks

Execute the following commands to verify system health:

### 1. API Root Verification
```bash
curl http://localhost:8000/
```
**Expected Response:** `{"name": "ApplyForge API", "status": "running"}`

### 2. Infrastructure Health Check
```bash
curl http://localhost:8000/admin/health
```
**Expected Response:** `{"status": "ok", "database": "ok", "redis": "ok"}`

### 3. Service Visibility
- Open `http://localhost:3000` to verify the Web App loads.
- Open `http://localhost:5555` to verify Flower displays active Celery workers.

---

## Useful Docker Commands

**Start in the background (Detached mode):**
```bash
cd infra
docker compose up --build -d
```

**Follow live logs:**
```bash
cd infra
docker compose logs -f api worker web
```

**Stop the stack gracefully:**
```bash
cd infra
docker compose down
```

**Stop the stack and wipe all database volumes (Hard Reset):**
```bash
cd infra
docker compose down -v
```

---

## Common Local Testing Workflow

To thoroughly test the application locally, follow this sequence:

1. Seed the demo data.
2. Log into the Web App.
3. Navigate to `/wizard` and verify system readiness.
4. Upload a sample resume.
5. Create a target role and execute a manual scrape run.
6. Verify jobs populate the feed correctly.
7. Tailor a resume to a specific job and export the PDF.
8. Initiate a draft or assisted application run.
9. Review `/admin` and `/runs/[id]` to inspect the generated logs and screenshots.

---

## Local OAuth Configuration Notes

If you intend to test Gmail or Outlook integrations locally, your `apps/api/.env` file must contain valid OAuth credentials.

**Required Local Callback URIs:**
- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

*Ensure your external OAuth provider app registrations strictly match these URIs.*

---

## Troubleshooting Guide

### Port Binding Conflicts
If ports `3000`, `5432`, `6379`, `8000`, or `5555` are already in use, you must stop the conflicting host process or adjust the published port mappings within `infra/docker-compose.yml`.

### Worker Stagnation
If tasks are not processing, inspect the worker and Redis logs:
```bash
cd infra
docker compose logs -f worker redis
```

### Database Schema Mismatches
Because the API utilizes `create_all` on startup, older local database volumes may become incompatible with new schema changes. If you encounter database errors immediately upon startup, perform a hard reset:
```bash
cd infra
docker compose down -v
docker compose up --build
```
*(Remember to re-run the seed command afterward.)*

### OAuth Connection Failures
If the settings page indicates a provider is not configured, double-check your `apps/api/.env` file to ensure the `CLIENT_ID` and `CLIENT_SECRET` variables for Google or Microsoft are correctly populated.

---

## Related Documentation

- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Project README](../README.md)
