# ApplyForge Local Docker Setup

## Purpose

This guide is the fastest way to run ApplyForge locally with Docker.

Use this if you want:

- the full web + API + worker stack
- PostgreSQL and Redis included
- local manual testing without installing Python and Node on the host

## What Starts

The checked-in [docker-compose.yml](../infra/docker-compose.yml) starts:

- `db` on `5432`
- `redis` on `6379`
- `api` on `8000`
- `web` on `3000`
- `flower` on `5555`
- `worker` as a background service

## Important Local Behavior

The current Compose file is development-oriented:

- it mounts the source tree into the containers
- it reads the example env files first, then optional real local env files if they exist
- the web container runs the Next.js dev server
- the API creates tables at startup

That is acceptable for local testing. It is not the same thing as a hardened production deployment.

## Prerequisites

- Docker
- Docker Compose

Verify:

```bash
docker --version
docker compose version
```

## Option 1: Fastest Local Startup

This uses the checked-in example env files as they are.

```bash
cd infra
docker compose up --build
```

Then open:

- web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

This is the quickest path for a first local test.

If you are opening the stack from another machine on the same network, replace `localhost` with your Docker host IP.

For your current host that means:

- web: `http://172.24.28.220:3000`
- API docs: `http://172.24.28.220:8000/docs`
- Flower: `http://172.24.28.220:5555`

Important:

- `6379` is the Redis port, not the API port
- Redis is not an HTTP service
- the correct Redis URL is `redis://172.24.28.220:6379/0`, not `http://172.24.28.220:6379/`

## Option 2: Local Startup With Your Own Env Values

If you want real local secrets or OAuth credentials, create local env files first:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
cp infra/.env.example infra/.env
```

Then set the host IP in `infra/.env`:

```bash
PUBLIC_HOST=172.24.28.220
```

Then start:

```bash
cd infra
docker compose up --build
```

With `PUBLIC_HOST=172.24.28.220`, the browser-facing URLs become:

- web: `http://172.24.28.220:3000`
- API docs: `http://172.24.28.220:8000/docs`
- Flower: `http://172.24.28.220:5555`

Docker-internal traffic still uses service names:

- Postgres: `db:5432`
- Redis: `redis:6379`

## Seed Demo Data

Once the stack is up, seed demo data from another terminal:

```bash
cd infra
docker compose exec api python -m app.db.seed
```

First local login credentials:

- email: `defaultuser@applyforge.dev`
- password: `defaultuser123`

That bootstrap account is enabled only by local Docker Compose. It is no longer on by default in generic non-production environments.

## Smoke Check

Run these after startup:

### API root

```bash
curl http://localhost:8000/
```

Expected shape:

- `name` = `ApplyForge API`
- `status` = `running`

### Health

```bash
curl http://localhost:8000/admin/health
```

Expected shape:

- `status` = `ok`
- `database` = `ok`
- `redis` = `ok`

### Web

Open:

```text
http://localhost:3000
```

### Worker visibility

Open:

```text
http://localhost:5555
```

Flower should show the Celery worker if startup succeeded.

If you are testing from another machine on the network, use:

- API root: `http://172.24.28.220:8000/`
- health: `http://172.24.28.220:8000/admin/health`
- web: `http://172.24.28.220:3000`
- Flower: `http://172.24.28.220:5555`

## Useful Local Commands

Start in background:

```bash
cd infra
docker compose up --build -d
```

Follow logs:

```bash
cd infra
docker compose logs -f api worker web
```

Stop the stack:

```bash
cd infra
docker compose down
```

Stop and remove volumes:

```bash
cd infra
docker compose down -v
```

Use `down -v` only if you want to reset local PostgreSQL data.

## Common Local Test Flow

After startup:

1. Seed demo data.
2. Log in through the web app.
3. Open `/wizard` and verify readiness.
4. Upload a resume.
5. Create a role and run a scrape.
6. Confirm jobs appear.
7. Tailor a resume and export PDF.
8. Start a draft or assisted application run.
9. Check `/admin` and `/runs/[id]` for logs and screenshots.

## Local OAuth Notes

If you want Gmail or Outlook connect to work locally, the API env must include valid OAuth credentials.

Recommended local callback URIs:

- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

The provider app registration must match those URIs exactly.

## Troubleshooting

### Port already in use

If `3000`, `5432`, `6379`, `8000`, or `5555` is already taken, stop the conflicting process or change the published port mapping in [docker-compose.yml](../infra/docker-compose.yml).

### Worker not processing tasks

Check:

```bash
cd infra
docker compose logs -f worker redis
```

### API starts but schema looks wrong

The API currently creates tables at startup, but older local databases may still be incompatible with new columns.

If needed, reset local state:

```bash
cd infra
docker compose down -v
docker compose up --build
```

Then reseed.

### OAuth button shows provider not configured

Make sure your API env file includes:

- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`
- or `MICROSOFT_OAUTH_CLIENT_ID` and `MICROSOFT_OAUTH_CLIENT_SECRET`

## Related Docs

- [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md)
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- [README.md](../README.md)
