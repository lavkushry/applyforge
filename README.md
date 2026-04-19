# ApplyForge

**Your AI Job Hunt Operating System**

ApplyForge is a production-minded MVP monorepo built for end-to-end job search operations. It seamlessly combines resume intelligence, job discovery, fit scoring, tailored document generation, and guarded browser automation into one unified product scaffold.

## Final Architecture Overview

- **`apps/web`**: Next.js + TypeScript application powering marketing pages, dashboards, profile editing, job listings, trackers, and diagnostics.
- **`apps/api`**: FastAPI + SQLAlchemy service handling authentication, profile/resume workflows, job normalization, scoring, tailoring, files, and application state.
- **`apps/worker`**: Celery + Playwright executor with a step-based assisted-apply skeleton that reliably captures screenshots and handles pause points.
- **`packages/prompts`**: Core prompt templates for resume cleanup, job normalization, scoring, tailoring, cover letters, question answering, and risk detection.
- **`infra`**: Docker Compose and Dockerfiles for straightforward local orchestration.
- **`docs`**: Comprehensive architecture notes, TODOs, and product-operating documentation.
- **`.codex` and `.agents`**: Project-local agent roles and skills designed for future AI-assisted maintenance.

## Implementation Status

### Phase 1
- Email/password authentication featuring cookie-backed session tokens.
- Candidate profile CRUD operations alongside a resume upload/parse flow.
- Manual job ingestion complete with normalization and deduplication keys.
- Role scrape runs featuring discovery-first job insertion and worker-queued enrichment.
- Packaged discovery preset registry with example search templates, direct-site presets, and Workday-style source presets.
- Job scoring engine providing transparent reasons, enrichment revisions, and actionable recommendations.
- Core UI pages: Dashboard, jobs list, job detail, resume, and profile.

### Phase 2
- Tailored resume generation utilizing fact-locked content reuse.
- ATS-friendly PDF export for various resume versions.
- Packaged Markdown and LaTeX resume starter templates bundled with developer CLI helpers.
- Seamless cover-letter generation flow.
- Comprehensive applications tracker board and user settings page.

### Phase 3
- Step-based application run records with durably persisted statuses.
- Assisted and auto-run API flows featuring pause-before-submit behavior.
- Draft packet-review runs for thorough dry-run preparation.
- Playwright worker skeleton that captures screenshots and performs basic field filling.
- Run timeline and detailed diagnostics UI.
- Worker-backed job enrichment alongside score-change feed events.
- Apply control center providing pipeline-stage visibility and manual operator actions.
- Setup wizard page offering readiness checks and one-click role bootstrapping from packaged templates.
- Formal run-state transitions paired with a reusable user-preference export for automation.

### Phase 4 Foundations
- User-scoped company intelligence directory containing portals and key contacts.
- Resume template catalog and developer CLI deeply aligned with structured Markdown and LaTeX workflows.
- Portable automation preference export accessible within Settings.

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

## Quick Start Guide

### 1. Prerequisites

- Docker and Docker Compose
- Node.js 20+
- Python 3.12+

### 2. Environment Configuration

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Running with Docker

```bash
cd infra
docker compose up --build
```

**Services:**
- Web: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Flower: `http://localhost:5555`

### 4. Running Locally (Without Docker)

```bash
make setup
make dev
```

In a separate shell:
```bash
make seed
```

**First Local Login Credentials:**
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

## Discovery Presets & Wizard

ApplyForge ships with a small, packaged discovery registry inspired by the ApplyPilot config layout:

- `packages/config/discovery/employers.yaml`
- `packages/config/discovery/sites.yaml`
- `packages/config/discovery/searches.example.yaml`

These power:
- `GET /roles/source-presets`
- `GET /setup/wizard`
- `POST /setup/wizard/bootstrap-role`

In the web app:
- `/wizard` displays first-run readiness and recommends role templates.
- `/roles` allows users to attach packaged source presets (including Workday-style boards) without manual configuration.

## Inbox OAuth Integration

ApplyForge connects to Gmail or Outlook so application runs can automatically fetch OTP emails.

**Required API Environment Variables (in `apps/api/.env`):**
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

**Recommended Local Redirect URIs:**
- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

**Required Provider Scopes:**
- Gmail: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- Outlook: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

Once configured, use the OAuth connect buttons on the web app's Settings page, which also highlights missing environment variables.

## Resume Template Catalog & CLI

ApplyForge includes a packaged resume-template layer modeled after ResumeCraftr:

- `packages/config/resume/sections.json`
- `packages/config/resume/resume_template.md`
- `packages/config/resume/resume_template.tex`

These power:
- `GET /resume/templates`
- `POST /resume/templates/render`
- `python -m app.cli.main list-templates`
- `python -m app.cli.main render-template --input /path/to/resume.json --template-key ats-markdown-starter`

In the web app:
- `/resume` lets users browse Markdown/LaTeX starter templates and render them using their canonical profile.
- The main PDF export still uses the standard export pipeline, maintaining RenderCV compatibility alongside an internal fallback.

## Automation Preferences & FSM

ApplyForge implements Jobber-style portable user preferences and a formal state machine for application runs:

- `GET /profile/preferences/export?format=text`
- `GET /profile/preferences/export?format=json`
- `apps/api/app/services/user_preferences.py`
- `apps/api/app/services/application_fsm.py`

In the web app:
- `/settings` displays an exported automation preference profile merging canonical data, saved answers, roles, keywords, and resume defaults.
- Application runs strictly follow transition rules for `queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`.

## Documentation Map

- **[docs/LOCAL_DOCKER.md](docs/LOCAL_DOCKER.md):** Full-stack Docker startup, seed flow, smoke checks, and troubleshooting.
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md):** Deployment topology, env setup, smoke checks, and rollout notes.
- **[docs/REQUIREMENTS.md](docs/REQUIREMENTS.md):** Current product requirements and core invariants.
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md):** Runtime architecture and data flow.
- **[docs/CONTEXT.md](docs/CONTEXT.md):** Fast orientation guide for future work.
- **[docs/TODO.md](docs/TODO.md):** Remaining hardening tasks and future roadmap.
- **[docs/FEATURE_REQUESTS/applypilot-core-roadmap.md](docs/FEATURE_REQUESTS/applypilot-core-roadmap.md):** ApplyPilot-style roadmap status.
- **[docs/IDEAS/company-intelligence-directory.md](docs/IDEAS/company-intelligence-directory.md):** Status of the company directory feature.

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

- Resume tailoring never fabricates facts and always preserves fact-locked sections.
- Unknown application questions immediately return `Requires candidate review`.
- Risky questions (e.g., salary, visa) strictly force manual approval.
- Automation runs reliably persist step logs, retry counts, timestamps, and structured outputs.

## Current Gaps

- Full Alembic revision history is scaffolded but not entirely authored.
- Job enrichment is worker-queued, but retry/backoff observability remains limited.
- Frontend document editing is MVP-grade; it needs richer section editors.
- Enterprise features (multi-user, agency workflows, S3 storage) are slated for future phases.

See the full documentation mapped above for additional technical depth and orientation.
