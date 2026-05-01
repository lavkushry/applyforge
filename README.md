# ApplyForge 🚀

**Your AI-Powered Job Hunt Operating System**

Welcome to ApplyForge! ApplyForge is a production-minded MVP monorepo built to streamline your end-to-end job search operations. It seamlessly combines resume intelligence, job discovery, fit scoring, tailored document generation, and guarded browser automation into a single, cohesive product scaffold.

## 🏗️ Architecture at a Glance

ApplyForge is structured across several key components:

- **`apps/web`**: A robust Next.js + TypeScript application powering the marketing pages, dashboard, profile editing, job discovery, application tracker, and diagnostic tools.
- **`apps/api`**: A blazing-fast FastAPI + SQLAlchemy backend service handling authentication, profile/resume workflows, job normalization, fit scoring, document tailoring, file management, and application run states.
- **`apps/worker`**: A reliable Celery + Playwright executor featuring a step-based assisted-apply skeleton. It ensures accurate execution while capturing crucial screenshots and respecting pause points.
- **`packages/prompts`**: A collection of finely-tuned prompt templates for resume cleanup, job normalization, scoring, tailoring, cover letter generation, and risk detection.
- **`infra`**: Ready-to-use Docker Compose setups and Dockerfiles for seamless local orchestration.
- **`docs`**: Comprehensive architecture notes, TODOs, and operational product documentation.
- **`.codex` and `.agents`**: Project-local agent roles and skills configured for future AI-assisted maintenance and operations.

---

## 🎯 What Is Implemented

ApplyForge has been developed in focused phases. Here is what is ready to use today:

### Phase 1: Core Foundations
- Secure email/password authentication using a cookie-backed session token.
- Full CRUD operations for candidate profiles, paired with a robust resume upload and parsing flow.
- Manual job ingestion complete with normalization and unique deduplication keys.
- Scheduled role scrape runs, prioritizing job discovery and queuing worker-based enrichment.
- A packaged discovery preset registry, including example search templates, direct-site presets, and Workday-style source configurations.
- An intelligent job scoring engine providing transparent reasons, enrichment revisions, and actionable recommendations.
- Essential user interfaces: Dashboard, Jobs List, Job Detail, Resume Builder, and Profile Editor pages.

### Phase 2: Document Generation
- Dynamic, tailored resume generation ensuring fact-locked content reuse.
- High-quality, ATS-friendly PDF exports for all resume versions.
- A suite of packaged Markdown and LaTeX resume starter templates, supported by developer CLI helpers.
- Automated cover letter generation tailored to specific roles.
- A comprehensive applications tracker board and configurable settings page.

### Phase 3: Automation & Execution
- Step-based application run records maintaining persisted operational statuses.
- Assisted and auto-run API workflows featuring critical pause-before-submit behaviors for safety.
- Draft packet-review runs allowing for risk-free dry-run preparations.
- A Playwright worker skeleton capable of capturing visual evidence (screenshots) and handling basic field filling.
- A detailed run timeline and diagnostics UI for transparent operation tracking.
- Worker-backed job enrichment loops and score-change feed events.
- A centralized Application Control Center providing pipeline-stage visibility and manual operator overrides.
- A guided setup wizard page featuring readiness checks and one-click role bootstrapping from packaged templates.
- Formal run-state machine transitions, alongside a reusable user-preference export tool for external automation.

### Phase 4: Intelligence Foundations
- A user-scoped company intelligence directory tracking career portals and recruitment contacts.
- A curated resume template catalog and developer CLI deeply integrated with structured Markdown and LaTeX workflows.
- Portable automation preference exports seamlessly accessible via the Settings interface.

---

## 📂 Monorepo Layout

```text
/apps
  ├── api
  ├── web
  └── worker
/packages
  ├── config
  ├── prompts
  ├── shared
  ├── types
  └── ui
/infra
/docs
/.codex
/.agents
```

---

## 🚀 Quick Start

Get ApplyForge up and running locally in minutes.

### 1. Prerequisites

Ensure you have the following installed on your system:
- **Docker + Docker Compose**
- **Node.js 20+**
- **Python 3.12+**

### 2. Environment Setup

Copy the example environment files to their active locations:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Start the Stack (with Docker)

Launch the entire stack using Docker Compose:

```bash
cd infra
docker compose up --build
```

**Accessing Services:**
- **Web App:** `http://localhost:3000`
- **API Documentation:** `http://localhost:8000/docs`
- **Flower (Celery Monitor):** `http://localhost:5555`

### 4. Start Locally (without Docker)

If you prefer to run the services natively:

```bash
make setup
make dev
```

In a separate terminal shell, seed the database with initial data:

```bash
make seed
```

**First Local Login Credentials:**
- **Email:** `defaultuser@applyforge.dev`
- **Password:** `defaultuser123`

---

## 🧭 Discovery Presets and Wizard

ApplyForge ships with a streamlined, packaged discovery registry inspired by ApplyPilot's configuration layout:

- `packages/config/discovery/employers.yaml`
- `packages/config/discovery/sites.yaml`
- `packages/config/discovery/searches.example.yaml`

These configurations power the following features:
- `GET /roles/source-presets`
- `GET /setup/wizard`
- `POST /setup/wizard/bootstrap-role`

**In the Web App:**
- `/wizard` guides you through first-run readiness and suggests recommended role templates.
- `/roles` allows you to effortlessly attach packaged source presets (including complex Workday-style boards) without manual configuration.

---

## 📧 Inbox OAuth Setup

ApplyForge can securely connect to Gmail or Outlook to automatically fetch OTP (One-Time Password) emails during application runs.

**Required API Environment Variables (`apps/api/.env`):**
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

**Recommended Local Redirect URIs:**
- **Google:** `http://localhost:8000/inbox/gmail/oauth/callback`
- **Microsoft:** `http://localhost:8000/inbox/outlook/oauth/callback`

**Required Provider Scopes:**
- **Gmail:** `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- **Outlook:** `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

Once configured, navigate to **Settings** in the web app and use the OAuth connect buttons. The settings page clearly displays provider configuration status and alerts you to any missing environment variables.

---

## 📄 Resume Template Catalog and CLI

ApplyForge includes a streamlined resume-template layer inspired by ResumeCraftr's asset structure:

- `packages/config/resume/sections.json`
- `packages/config/resume/resume_template.md`
- `packages/config/resume/resume_template.tex`

These assets power the following endpoints and tools:
- `GET /resume/templates`
- `POST /resume/templates/render`
- `python -m app.cli.main list-templates`
- `python -m app.cli.main render-template --input /path/to/resume.json --template-key ats-markdown-starter`

**In the Web App:**
- `/resume` allows you to browse Markdown and LaTeX starter templates and instantly render them using your canonical profile data.
- The primary PDF export path leverages the product's robust resume export pipeline, ensuring RenderCV compatibility with a reliable internal fallback.

---

## ⚙️ Automation Preferences and State Machine

ApplyForge incorporates a formal application run state machine (FSM) and portable user preferences, similar to Jobber:

- `GET /profile/preferences/export?format=text`
- `GET /profile/preferences/export?format=json`
- `apps/api/app/services/user_preferences.py`
- `apps/api/app/services/application_fsm.py`

**In the Web App:**
- `/settings` displays an exportable automation preference profile, combining your canonical profile data, saved answers, target roles, keyword filters, and resume defaults.
- Application runs are governed by strict, explicit transition rules: `queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`.

---

## 📚 Documentation Map

Dive deeper into ApplyForge's architecture and operational guides:

- [**docs/LOCAL_DOCKER.md**](./docs/LOCAL_DOCKER.md): Local full-stack Docker startup, seed flows, smoke checks, and troubleshooting.
- [**docs/DEPLOYMENT.md**](./docs/DEPLOYMENT.md): Deployment topology, environment setup, smoke checks, and rollout caveats.
- [**docs/REQUIREMENTS.md**](./docs/REQUIREMENTS.md): Current product requirements and system invariants.
- [**docs/ARCHITECTURE.md**](./docs/ARCHITECTURE.md): Runtime and data-flow architecture overview.
- [**docs/CONTEXT.md**](./docs/CONTEXT.md): A rapid orientation guide for future development sessions.
- [**docs/TODO.md**](./docs/TODO.md): Remaining system hardening and follow-on feature work.
- [**docs/FEATURE_REQUESTS/applypilot-core-roadmap.md**](./docs/FEATURE_REQUESTS/applypilot-core-roadmap.md): Status of the core roadmap.
- [**docs/IDEAS/company-intelligence-directory.md**](./docs/IDEAS/company-intelligence-directory.md): Status of the company directory foundation.

---

## 🛠️ Useful Commands

Common development operations available via `make`:

```bash
make api              # Start API server locally
make web              # Start Web server locally
make worker           # Start Celery worker locally
make api-test         # Run API test suite
make web-typecheck    # Run Web TypeScript checks
make lint             # Run linters across the repo
```

---

## 🛡️ Core Safety Rules

ApplyForge is built with strict adherence to data integrity and user safety:

1. **Absolute Truth:** Resume tailoring algorithms will **never** invent facts. Fact-locked sections are strictly preserved.
2. **Safety First:** Unknown or unanswerable application questions default to a `Requires candidate review` status.
3. **Risk Mitigation:** Risky prompts (e.g., salary expectations, visa status) immediately force manual user approval.
4. **Transparent Automation:** All automation runs meticulously persist step logs, retry counts, timestamps, and structured outputs for full auditability.

---

## 🚧 Current Gaps & Future Work

While highly functional, some areas are still evolving:
- The full Alembic database revision history is scaffolded but not entirely authored.
- Job enrichment is queued effectively, but deeper retry/backoff observability is needed.
- Frontend document editing is at an MVP grade and will benefit from richer, more interactive section editors in the future.
- Enterprise multi-user support, agency workflows, and dedicated S3 storage integrations are slated for subsequent phases.

For a deeper dive into what's next, consult [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md), [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md), and [docs/TODO.md](./docs/TODO.md). Need a quick refresher? Start with [docs/CONTEXT.md](./docs/CONTEXT.md).
