# ApplyForge Local Docker Setup Guide

## 🎯 Purpose

This guide provides the fastest and most reliable path to run the complete ApplyForge stack locally using Docker.

Use this approach if you want:
- The full Web + API + Worker stack running simultaneously.
- Zero-configuration PostgreSQL and Redis instances.
- To perform manual end-to-end testing without installing Python, Node.js, or Playwright on your host machine.

---

## 🏗️ What Starts Up

When you run the provided `docker-compose.yml`, the following services are spun up:

- **`db`**: PostgreSQL running on port `5432`.
- **`redis`**: Redis instance running on port `6379`.
- **`api`**: FastAPI backend running on port `8000`.
- **`web`**: Next.js frontend running on port `3000`.
- **`flower`**: Celery monitoring dashboard on port `5555`.
- **`worker`**: Background Celery process executing tasks.

---

## ⚠️ Important Local Behavior Caveats

The current Docker Compose configuration is heavily optimized for **development**, not production:

- **Volume Mounts:** It mounts your local source tree directly into the containers, allowing for live-reloading.
- **Environment Fallback:** It defaults to reading `.env.example` files if real `.env` files are missing.
- **Development Server:** The `web` container executes the Next.js development server (`npm run dev`), which is significantly slower than a production build.
- **Auto-Migrations:** The `api` container automatically creates database tables on startup.

*This setup is perfect for local testing but should never be deployed publicly as-is.*

---

## ✅ Prerequisites

Ensure the following tools are installed and running on your host machine:

- **Docker**
- **Docker Compose**

Verify your installation:
```bash
docker --version
docker compose version
```

---

## 🚀 Option 1: Fastest Local Startup (Using Example Env)

This is the quickest path for a first-time local test. It uses the checked-in `.env.example` files as they are.

```bash
cd /home/ems/applyforge/infra
docker compose up --build
```

Once the terminal output stabilizes, access the services:
- **Web App:** `http://localhost:3000`
- **API Swagger Docs:** `http://localhost:8000/docs`
- **Flower Dashboard:** `http://localhost:5555`

### Testing from another machine on the same network:
Replace `localhost` with your Docker host's IP address (e.g., `172.24.28.220`).
- **Web App:** `http://172.24.28.220:3000`
- **API Docs:** `http://172.24.28.220:8000/docs`

*Note on Redis: Redis uses port `6379`, but it is not an HTTP service. Do not attempt to access it via a web browser.*

---

## 🔐 Option 2: Startup With Custom/Real Env Values

If you need to test features requiring real credentials (like OpenAI keys or OAuth for Gmail/Outlook), you must create and populate local `.env` files.

### 1. Copy Environment Files
```bash
cp /home/ems/applyforge/apps/api/.env.example /home/ems/applyforge/apps/api/.env
cp /home/ems/applyforge/apps/web/.env.example /home/ems/applyforge/apps/web/.env.local
cp /home/ems/applyforge/apps/worker/.env.example /home/ems/applyforge/apps/worker/.env
cp /home/ems/applyforge/infra/.env.example /home/ems/applyforge/infra/.env
```

### 2. Configure Host IP (Optional)
If accessing from a network, set your host IP in `/home/ems/applyforge/infra/.env`:
```bash
PUBLIC_HOST=172.24.28.220
```

### 3. Start the Stack
```bash
cd /home/ems/applyforge/infra
docker compose up --build
```

*Note: Docker-internal traffic will still seamlessly route using service names (`db:5432`, `redis:6379`), regardless of the `PUBLIC_HOST` setting.*

---

## 🌱 Seed Demo Data

Once the Docker stack is fully operational, open a *new* terminal window and seed the database to easily begin testing:

```bash
cd /home/ems/applyforge/infra
docker compose exec api python -m app.db.seed
```

**First Local Login Credentials:**
- **Email:** `defaultuser@applyforge.dev`
- **Password:** `defaultuser123`

*(Note: This bootstrap account is strictly enabled only in local development environments.)*

---

## 🔍 Smoke Checks

Run these rapid checks to confirm system health:

### 1. API Root Check
```bash
curl http://localhost:8000/
```
*Expected Output:* `{"name": "ApplyForge API", "status": "running"}`

### 2. Deep Health Check
```bash
curl http://localhost:8000/admin/health
```
*Expected Output:* `{"status": "ok", "database": "ok", "redis": "ok"}`

### 3. Visual Checks
- Open `http://localhost:3000` to verify the frontend loads.
- Open `http://localhost:5555` to verify the Celery worker is registered and visible in Flower.

---

## ⌨️ Useful Local Commands

**Start in the background (Detached mode):**
```bash
cd /home/ems/applyforge/infra
docker compose up --build -d
```

**Follow active logs:**
```bash
cd /home/ems/applyforge/infra
docker compose logs -f api worker web
```

**Gracefully stop the stack:**
```bash
cd /home/ems/applyforge/infra
docker compose down
```

**Stop the stack and wipe the database (Hard Reset):**
```bash
cd /home/ems/applyforge/infra
docker compose down -v
```
*Warning: This will permanently delete all local PostgreSQL data and uploaded files.*

---

## 🧪 Common Local Test Flow

To fully exercise the system locally, follow this sequence:

1. Seed the demo data via the `docker compose exec api` command.
2. Log in to the web app using `defaultuser@applyforge.dev`.
3. Navigate to `/wizard` and verify system readiness.
4. Upload a test resume PDF.
5. Create a target role and initiate a job scrape.
6. Confirm that scraped jobs successfully appear in the feed.
7. Trigger resume tailoring and export the resulting PDF.
8. Start a draft or assisted application run.
9. Navigate to `/admin` and `/runs/[id]` to review captured logs and Playwright screenshots.

---

## 📧 Local OAuth Notes (Gmail / Outlook)

For local Inbox OAuth testing to succeed, the API environment (`apps/api/.env`) must contain valid OAuth credentials matching your cloud provider setup.

**Required Local Callback URIs:**
- **Google:** `http://localhost:8000/inbox/gmail/oauth/callback`
- **Microsoft:** `http://localhost:8000/inbox/outlook/oauth/callback`

*These exact URIs must be registered in your Google Cloud Console or Azure AD application settings.*

---

## 🚑 Troubleshooting

### "Port already in use" Error
If ports `3000`, `5432`, `6379`, `8000`, or `5555` are taken, you must either terminate the conflicting host process or manually adjust the published port mappings in `infra/docker-compose.yml`.

### Worker is Not Processing Tasks
Check the worker and redis logs for connection issues or task timeouts:
```bash
cd /home/ems/applyforge/infra
docker compose logs -f worker redis
```

### API Starts, but the Schema Looks Wrong
Because the API relies on auto-creating tables at startup, legacy database volumes from older branches can conflict with new schema designs.
**Fix:** Perform a hard reset to wipe the old volume.
```bash
cd /home/ems/applyforge/infra
docker compose down -v
docker compose up --build
```
*(Remember to re-run the seed command afterward).*

### OAuth Button Reports "Provider Not Configured"
Verify that your `apps/api/.env` file correctly contains:
- `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`
- OR `MICROSOFT_OAUTH_CLIENT_ID` and `MICROSOFT_OAUTH_CLIENT_SECRET`
Ensure Docker has picked up the changes by restarting the API container.