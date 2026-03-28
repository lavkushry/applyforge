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
- Role scrape runs with discovery-first job insertion and worker-queued enrichment.
- Packaged discovery preset registry with example search templates, direct-site presets, and Workday-style source presets.
- Job scoring engine with transparent reasons, enrichment revisions, and recommendations.
- Dashboard, jobs list, job detail, resume, and profile pages.

### Phase 2
- Tailored resume generation with fact-locked content reuse.
- ATS-friendly PDF export for resume versions.
- Packaged Markdown and LaTeX resume starter templates plus developer CLI helpers.
- Cover-letter generation flow.
- Applications tracker board and settings page.

### Phase 3
- Step-based application run records with persisted statuses.
- Assisted and auto-run API flows with pause-before-submit behavior.
- Draft packet-review runs for dry-run preparation.
- Playwright worker skeleton with screenshots and basic field filling.
- Run timeline and diagnostics UI.
- Worker-backed job enrichment and score-change feed events.
- Apply control center with pipeline-stage visibility and manual operator actions.
- Setup wizard page with readiness checks and one-click role bootstrapping from packaged templates.

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

## Discovery Presets And Wizard

ApplyForge now ships a small packaged discovery registry inspired by the ApplyPilot-style config layout.

- `packages/config/discovery/employers.yaml`
- `packages/config/discovery/sites.yaml`
- `packages/config/discovery/searches.example.yaml`

These power:

- `GET /roles/source-presets`
- `GET /setup/wizard`
- `POST /setup/wizard/bootstrap-role`

In the web app:

- `/wizard` shows first-run readiness and recommended role templates.
- `/roles` lets you attach a packaged source preset, including Workday-style boards, without manually copying config.

## Inbox OAuth Setup

ApplyForge can connect Gmail or Outlook so application runs can fetch OTP emails directly.

Required API env vars in [apps/api/.env.example](/home/ems/applyforge/apps/api/.env.example):

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

Recommended local redirect URIs:

- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

Required provider scopes:

- Gmail: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- Outlook: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

After those values are set, open Settings in the web app and use the OAuth connect buttons. The settings page now shows whether each provider is configured and which env vars are still missing.

## Resume Template Catalog And CLI

ApplyForge now ships a small packaged resume-template layer inspired by ResumeCraftr-style source assets:

- `packages/config/resume/sections.json`
- `packages/config/resume/resume_template.md`
- `packages/config/resume/resume_template.tex`

These power:

- `GET /resume/templates`
- `POST /resume/templates/render`
- `python -m app.cli.main list-templates`
- `python -m app.cli.main render-template --input /path/to/resume.json --template-key ats-markdown-starter`

In the web app:

- `/resume` now lets a user browse Markdown and LaTeX starter templates and render them from the current canonical profile.
- the main PDF export path still uses the product's resume export pipeline, including RenderCV compatibility plus internal fallback.

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
- Job enrichment is queued into the worker, but retry/backoff observability for enrichment tasks is still thin.
- Frontend document editing is MVP-grade and will benefit from richer section editors.
- Enterprise multi-user, agency workflows, and S3 storage remain future phases.

See [docs/ARCHITECTURE.md](/home/ems/applyforge/docs/ARCHITECTURE.md), [docs/REQUIREMENTS.md](/home/ems/applyforge/docs/REQUIREMENTS.md), and [docs/TODO.md](/home/ems/applyforge/docs/TODO.md) for more detail.
For fast future orientation, also see [docs/CONTEXT.md](/home/ems/applyforge/docs/CONTEXT.md).
