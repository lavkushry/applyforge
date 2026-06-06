# Quickstart: Local Docker Deployment

## Overview
This guide provides the fastest method to spin up ApplyForge locally utilizing Docker. It instantiates the complete stack (Web, API, Worker, PostgreSQL, Redis, and Flower) without needing host installations of Node or Python.

## Core Containers (`infra/docker-compose.yml`)
- **Web App**: Port `3000`
- **FastAPI Backend**: Port `8000`
- **PostgreSQL**: Port `5432`
- **Redis Cache/Broker**: Port `6379`
- **Flower (Celery Dashboard)**: Port `5555`
- **Celery Worker**: Background task processor

## Requirements
- Docker
- Docker Compose

## Booting the Stack

### Standard Boot (Using .env.example)
```bash
cd infra
docker compose up --build
```
Access points:
- Web: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

### Custom Env Boot
If you are binding specific IPs or using real OAuth credentials:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
cp infra/.env.example infra/.env
```
Ensure `PUBLIC_HOST` is correctly mapped in `infra/.env` (e.g., `PUBLIC_HOST=172.24.28.220`).
Start the stack:
```bash
cd infra
docker compose up --build
```

## Seeding the Database
To populate demo data, run in a separate terminal:
```bash
cd infra
docker compose exec api python -m app.db.seed
```
Login with `defaultuser@applyforge.dev` / `defaultuser123`.

## Smoke Testing
- API Root: `curl http://localhost:8000/` should return `{ "status": "running" }`
- Diagnostics: `curl http://localhost:8000/admin/health` should report `ok` statuses for DB and Redis.

## Maintenance Commands
- Detached Run: `docker compose up --build -d`
- Tailing Logs: `docker compose logs -f api worker web`
- Teardown: `docker compose down`
- Teardown w/ Volume Reset (Wipes DB): `docker compose down -v`

## Troubleshooting
- **Port Conflicts**: Terminate conflicting host services or modify bindings in `docker-compose.yml`.
- **Worker Hangs**: Inspect logs via `docker compose logs -f worker redis`.
- **Database Drift**: In development, schema drift might require wiping volumes (`docker compose down -v`).