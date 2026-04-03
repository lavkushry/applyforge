# Running ApplyForge Locally via Docker

This document provides a fast-track guide to booting the entire ApplyForge ecosystem locally using Docker Compose.

This approach spins up the Web UI, the API, the Celery Worker, PostgreSQL, and Redis simultaneously without requiring native Node.js or Python installations on your host machine.

## Container Architecture Overview

The provided `docker-compose.yml` provisions the following networked services:
- **`db`**: PostgreSQL instance exposed on port `5432`
- **`redis`**: Redis instance exposed on port `6379`
- **`api`**: FastAPI backend exposed on port `8000`
- **`web`**: Next.js frontend exposed on port `3000`
- **`flower`**: Celery monitoring tool exposed on port `5555`
- **`worker`**: Background task processor (no exposed port)

*Note: This specific Compose configuration is optimized for development. It utilizes live volume mounts for code hot-reloading and relies on placeholder `.env.example` files by default.*

## Quick Start (Zero Config)

If you just want to see the UI and test basic functionality, you can run the stack using the default example configurations.

1. Ensure Docker Engine and Compose are installed and running.
2. Navigate to the infrastructure folder and boot the cluster:
   ```bash
   cd infra
   docker compose up --build
   ```

Once the terminal output stabilizes, access the services:
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **API Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Worker Monitor**: [http://localhost:5555](http://localhost:5555)

*(If deploying on a remote local-network server, substitute `localhost` with your host machine's IP address).*

## Advanced Start (Custom Secrets & OAuth)

To test features relying on external APIs (like LLM tailoring or OAuth email connections), you must provide real environment variables.

1. Generate your local `.env` files from the templates:
   ```bash
   cp apps/api/.env.example apps/api/.env
   cp apps/web/.env.example apps/web/.env.local
   cp apps/worker/.env.example apps/worker/.env
   cp infra/.env.example infra/.env
   ```

2. *(Optional)* If accessing via LAN, specify the host IP in the infrastructure `.env`:
   ```bash
   echo "PUBLIC_HOST=192.168.1.100" >> infra/.env
   ```

3. Populate the `apps/api/.env` file with your actual `OPENAI_API_KEY` and OAuth client secrets.

4. Start the stack:
   ```bash
   cd infra
   docker compose up --build
   ```

## Bootstrapping Test Data

A completely fresh database contains no users or roles. To inject an initial testing profile, execute the seed command in a separate terminal while the cluster is running:

```bash
cd infra
docker compose exec api python -m app.db.seed
```

**Default Seed Credentials:**
- **Email:** `defaultuser@applyforge.dev`
- **Password:** `defaultuser123`

## Health Verification

To confirm the stack is operating correctly, query the internal health endpoint:

```bash
curl http://localhost:8000/admin/health
```
You should receive a JSON response indicating `"status": "ok"` alongside successful database and Redis connections.

## Everyday Developer Commands

**Run in detached mode (background):**
```bash
cd infra
docker compose up --build -d
```

**Stream logs for specific services:**
```bash
cd infra
docker compose logs -f api worker web
```

**Shut down gracefully:**
```bash
cd infra
docker compose down
```

**Nuke the database and start over (Destructive):**
```bash
cd infra
docker compose down -v
```

## Debugging Common Issues

- **Port Conflicts:** If ports `3000`, `8000`, or `5432` are in use by local host processes, you must terminate those host processes or modify the port bindings in `infra/docker-compose.yml`.
- **Silent Worker Failures:** If job enrichments or applications get stuck in `queued`, check the worker and redis logs specifically: `docker compose logs -f worker redis`.
- **Database Schema Errors:** If you pull new code containing database model changes, the automatic startup table creation might fail against an old volume. Run `docker compose down -v` to reset the database schema entirely.
- **OAuth Connect Buttons Disabled:** Ensure you have actually placed the Client ID and Secret pairs into `apps/api/.env` and restarted the API container.
