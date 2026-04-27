# ApplyForge Local Docker Setup Guide

This guide provides the fastest method for running the complete ApplyForge stack locally using Docker.

Use this approach if you want to quickly spin up the web frontend, API backend, worker nodes, PostgreSQL database, and Redis cache without needing to install Python or Node.js directly on your host machine.

## Architecture Started by Docker Compose

The included `infra/docker-compose.yml` orchestrates the following services:

*   **`db`**: PostgreSQL database exposed on port `5432`.
*   **`redis`**: Redis message broker exposed on port `6379`.
*   **`api`**: FastAPI backend service exposed on port `8000`.
*   **`web`**: Next.js frontend application exposed on port `3000`.
*   **`flower`**: Celery worker monitoring UI exposed on port `5555`.
*   **`worker`**: Celery + Playwright background task executor.

*Note: This configuration is optimized for local development. It mounts your source code directly into the containers, utilizes the Next.js development server, and automatically creates database tables upon API startup.*

## Prerequisites

Ensure the following tools are installed and operational on your machine:
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

Verify installation:
```bash
docker --version
docker compose version
```

## Quick Start (Default Environment)

If you simply want to test the application using the default configuration, follow these steps:

1.  Navigate to the infrastructure directory:
    ```bash
    cd infra
    ```

2.  Build and start the stack in detached mode:
    ```bash
    docker compose up --build -d
    ```

3.  Access the services:
    *   **Web App**: `http://localhost:3000`
    *   **API Docs**: `http://localhost:8000/docs`
    *   **Flower Dashboard**: `http://localhost:5555`

*(If you are running Docker on a remote host or virtual machine, replace `localhost` with your host's IP address).*

## Custom Setup (With Local Secrets)

If you need to test OAuth integrations or utilize specific environment variables, create custom `.env` files before starting:

1.  Copy the example environment files:
    ```bash
    cp apps/api/.env.example apps/api/.env
    cp apps/web/.env.example apps/web/.env.local
    cp apps/worker/.env.example apps/worker/.env
    cp infra/.env.example infra/.env
    ```

2.  (Optional) If running on a non-local network, update `PUBLIC_HOST` in `infra/.env` (e.g., `PUBLIC_HOST=192.168.1.50`).

3.  Start the stack:
    ```bash
    cd infra
    docker compose up --build -d
    ```

## Seeding Demo Data

Once the services are running, populate the database with initial demo data (including the default user account):

```bash
cd infra
docker compose exec api python -m app.db.seed
```

**Default Login Credentials:**
*   Email: `defaultuser@applyforge.dev`
*   Password: `defaultuser123`

## Smoke Testing the Deployment

After startup and seeding, run the following checks to ensure system health:

1.  **API Root**:
    ```bash
    curl http://localhost:8000/
    ```
    *Expected output includes `{"status": "running"}`.*

2.  **API Health Check**:
    ```bash
    curl http://localhost:8000/admin/health
    ```
    *Expected output includes `{"status": "ok", "database": "ok", "redis": "ok"}`.*

3.  **Web Interface**: Navigate to `http://localhost:3000` in your browser.

4.  **Worker Visibility**: Navigate to `http://localhost:5555` to confirm the Celery worker is registered in Flower.

## Common Operations

**View Logs:**
```bash
cd infra
docker compose logs -f api worker web
```

**Stop the Stack:**
```bash
cd infra
docker compose down
```

**Reset the Database (Deletes all local data):**
```bash
cd infra
docker compose down -v
```

## Local OAuth Configuration

To test Gmail or Outlook integrations locally, update `apps/api/.env` with your provider's credentials. Ensure your provider's app registration uses the following exact callback URIs:

*   **Google**: `http://localhost:8000/inbox/gmail/oauth/callback`
*   **Microsoft**: `http://localhost:8000/inbox/outlook/oauth/callback`

## Troubleshooting

*   **Port Conflicts**: If ports (3000, 5432, 6379, 8000, 5555) are in use, terminate the conflicting application or modify the port mappings in `docker-compose.yml`.
*   **Worker Inactive**: Check worker logs (`docker compose logs -f worker redis`) to diagnose connection issues.
*   **Database Schema Errors**: If the API fails due to schema mismatches (common during active development), perform a hard reset using `docker compose down -v` followed by `docker compose up --build` and re-run the seed command.
*   **OAuth UI Errors**: If the Settings page shows "Provider Not Configured", verify that `*_CLIENT_ID` and `*_CLIENT_SECRET` are correctly populated in `apps/api/.env`.
