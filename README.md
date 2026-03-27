# ApplyForge

Your AI Job Hunt Operating System

ApplyForge is a production-minded MVP monorepo for end-to-end job search operations. It combines resume intelligence, job discovery and fit scoring, tailored document generation, and guarded browser automation into a single product scaffold.

## Final Architecture

- `apps/web`: Next.js + TypeScript application for marketing pages, dashboard, profile editing, jobs, tracker, and diagnostics.
- `apps/api`: FastAPI + SQLAlchemy service for auth, profile/resume flows, job normalization, scoring, tailoring, files, and application run state.
- `apps/worker`: Celery + Playwright executor with a step-based assisted-apply skeleton that captures screenshots and pause points.
- `packages/prompts`: Prompt templates for resume cleanup, job normalization, scoring, tailoring, cover letters, answers, and risk detection.
- `infra`: Docker Compose and Dockerfiles for local orchestration.
- `docs`: Architecture notes, TODOs, and product-operating documentation.
- `.codex` and `.agents`: Project-local agent roles and skills for future AI-assisted maintenance.

## What Is Implemented

### Phase 1
- Email/password auth with cookie-backed session token.
- Candidate profile CRUD and resume upload/parse flow.
- Manual job ingestion with normalization and dedupe keys.
- Job scoring engine with transparent reasons and recommendations.
- Dashboard, jobs list, job detail, resume, and profile pages.

### Phase 2
- Tailored resume generation with fact-locked content reuse.
- ATS-friendly PDF export for resume versions.
- Cover-letter generation flow.
- Applications tracker board and settings page.

### Phase 3
- Step-based application run records with persisted statuses.
- Assisted and auto-run API flows with pause-before-submit behavior.
- Playwright worker skeleton with screenshots and basic field filling.
- Run timeline and diagnostics UI.

## Monorepo Layout

```text
/apps
  /api
  /web
  /worker
/packages
  /config
  /prompts
  /shared
  /types
  /ui
/infra
/docs
/.codex
/.agents
```

## Quick Start

### 1. Prerequisites

- Docker + Docker Compose
- Node.js 20+
- Python 3.12+

### 2. Environment

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Start the stack with Docker

```bash
cd infra
docker compose up --build
```

Services:

- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

### 4. Start locally without Docker

```bash
make setup
make dev
```

Then in a separate shell:

```bash
make seed
```

Demo credentials:

- Email: `demo@applyforge.dev`
- Password: `demo1234`

## Useful Commands

```bash
make api
make web
make worker
make api-test
make web-typecheck
make lint
```

## Core Safety Rules

- Resume tailoring never invents facts and preserves fact-locked sections.
- Unknown application questions return `Requires candidate review`.
- Risky questions such as salary or visa prompts force manual approval.
- Automation runs persist step logs, retry counts, timestamps, and structured outputs.

## Current Gaps

- Full Alembic revision history is scaffolded but not yet fully authored.
- Worker dispatch from the API is still inline/skeleton rather than fully queued.
- Frontend document editing is MVP-grade and will benefit from richer section editors.
- Enterprise multi-user, agency workflows, and S3 storage remain future phases.

See [docs/ARCHITECTURE.md](/home/ems/applyforge/docs/ARCHITECTURE.md) and [docs/TODO.md](/home/ems/applyforge/docs/TODO.md) for more detail.
