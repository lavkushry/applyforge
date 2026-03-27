# ApplyForge — Your AI Job Hunt Operating System

ApplyForge is a production-minded MVP monorepo for AI-assisted job search and application workflows.

## Monorepo Layout

- `apps/web`: Next.js frontend
- `apps/api`: FastAPI backend
- `apps/worker`: Celery worker + Playwright automation executor
- `packages/prompts`: prompt templates for AI tasks
- `infra`: Dockerfiles and docker-compose
- `docs`: architecture and roadmap

## Quick Start

### 1) Prerequisites
- Docker + Docker Compose
- Node.js 20+
- Python 3.12+

### 2) Environment
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3) Run full stack with Docker
```bash
cd infra
docker compose up --build
```

Services:
- Web: http://localhost:3000
- API: http://localhost:8000/docs
- Flower: http://localhost:5555

### 4) Local dev without Docker
```bash
make setup
make dev
```

## Seed Demo Data
```bash
make seed
```
Creates a default user, candidate profile, jobs, score snapshots, and one sample application run.

## Safety Rules in Code
- Resume tailoring is fact-locked against the canonical profile.
- Unknown application answers return `requires_review`.
- Automation run steps are persisted with status and retry counters.

## MVP Status
See `docs/TODO.md` for remaining hardening and edge cases.
