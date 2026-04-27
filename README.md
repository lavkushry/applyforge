# ApplyForge

**Your AI-Powered Job Hunt Operating System**

ApplyForge is a production-ready monorepo designed to manage your end-to-end job search operations. It seamlessly integrates resume intelligence, job discovery, fit scoring, tailored document generation, and guarded browser automation into a single, cohesive platform.

## Architecture Overview

ApplyForge consists of the following core components:

*   **`apps/web`**: A Next.js and TypeScript frontend application providing marketing pages, a user dashboard, profile editing, job listings, application tracking, and system diagnostics.
*   **`apps/api`**: A FastAPI and SQLAlchemy backend service handling authentication, profile and resume management, job normalization, scoring, document tailoring, file management, and application run state.
*   **`apps/worker`**: A Celery and Playwright task executor featuring a step-based, assisted-apply engine that captures screenshots and pause points during application submissions.
*   **`packages/prompts`**: Prompt templates utilized for resume refinement, job normalization, scoring, tailoring, cover letter generation, question answering, and risk detection.
*   **`infra`**: Docker Compose configurations and Dockerfiles for orchestrating local development environments.
*   **`docs`**: Comprehensive documentation covering architecture, requirements, deployment, and product roadmaps.
*   **`.codex` and `.agents`**: Project-local agent roles and skills to facilitate future AI-assisted development and maintenance.

## Implementation Phases

### Phase 1: Foundation and Discovery
*   Email/password authentication with secure, cookie-backed session tokens.
*   Comprehensive candidate profile management with automated resume parsing.
*   Manual job ingestion featuring data normalization and deduplication.
*   Automated role scraping with discovery-first job insertion and queued enrichment.
*   A packaged discovery preset registry, including search templates, direct-site presets, and Workday-style source configurations.
*   A robust job scoring engine providing transparent reasoning, enrichment revisions, and actionable recommendations.
*   Core UI elements: Dashboard, job listings, job details, resume viewer, and profile editor.

### Phase 2: Document Tailoring
*   Fact-locked tailored resume generation ensuring content accuracy.
*   ATS-friendly PDF export capabilities for resume versions.
*   Packaged Markdown and LaTeX resume starter templates supported by developer CLI helpers.
*   Automated cover letter generation workflows.
*   An interactive application tracking board and comprehensive user settings.

### Phase 3: Automation and Execution
*   Step-based application run records maintaining persistent status tracking.
*   Assisted and automated API application flows with pause-before-submit safeguards.
*   Draft packet-review runs allowing dry-run preparations.
*   Playwright worker implementation for capturing screenshots and performing basic field population.
*   Detailed run timelines and diagnostic UI for transparent operation.
*   Worker-backed job enrichment integrated with score-change feed events.
*   An Apply Control Center offering pipeline-stage visibility and manual operator interventions.
*   A guided setup wizard for initial readiness checks and one-click role bootstrapping from packaged templates.
*   Formal run-state transitions and reusable user-preference exports for enhanced automation.

### Phase 4: Intelligence and Refinement
*   A user-scoped company intelligence directory supporting portals and contacts.
*   A robust resume template catalog and developer CLI aligned with structured Markdown and LaTeX workflows.
*   Portable automation preference exports accessible via the Settings interface.

## Monorepo Structure

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

Ensure the following tools are installed:
*   Docker and Docker Compose
*   Node.js (v20 or higher)
*   Python (v3.12 or higher)

### 2. Environment Configuration

Copy the example environment files to their respective locations:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Running with Docker (Recommended)

Start the entire stack using Docker Compose:

```bash
cd infra
docker compose up --build
```

Access the services:
*   **Web Frontend**: `http://localhost:3000`
*   **API Documentation**: `http://localhost:8000/docs`
*   **Flower (Worker UI)**: `http://localhost:5555`

### 4. Running Locally (Without Docker)

To run the services natively:

```bash
make setup
make dev
```

In a separate terminal, seed the database:

```bash
make seed
```

**Default Local Credentials:**
*   Email: `defaultuser@applyforge.dev`
*   Password: `defaultuser123`

## Discovery Presets and Setup Wizard

ApplyForge includes a packaged discovery registry inspired by ApplyPilot configurations, located at:
*   `packages/config/discovery/employers.yaml`
*   `packages/config/discovery/sites.yaml`
*   `packages/config/discovery/searches.example.yaml`

These configurations power the API endpoints (`GET /roles/source-presets`, `GET /setup/wizard`, `POST /setup/wizard/bootstrap-role`) and the web UI (`/wizard`, `/roles`), enabling users to effortlessly attach packaged source presets.

## Inbox OAuth Integration

ApplyForge supports Gmail and Outlook integration to automatically fetch OTP (One-Time Password) emails during application runs.

**Required API Environment Variables (in `apps/api/.env`):**
*   `GOOGLE_OAUTH_CLIENT_ID`
*   `GOOGLE_OAUTH_CLIENT_SECRET`
*   `GOOGLE_OAUTH_REDIRECT_URI`
*   `MICROSOFT_OAUTH_CLIENT_ID`
*   `MICROSOFT_OAUTH_CLIENT_SECRET`
*   `MICROSOFT_OAUTH_TENANT`
*   `MICROSOFT_OAUTH_REDIRECT_URI`

**Recommended Local Redirect URIs:**
*   Google: `http://localhost:8000/inbox/gmail/oauth/callback`
*   Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

Configure the OAuth connection via the Settings page in the web app. The interface displays connection status and highlights any missing environment variables.

## Resume Template Catalog and CLI

A packaged resume-template layer (inspired by ResumeCraftr) is available at:
*   `packages/config/resume/sections.json`
*   `packages/config/resume/resume_template.md`
*   `packages/config/resume/resume_template.tex`

Users can browse and render Markdown/LaTeX templates via the web UI (`/resume`) or utilize the CLI tool:

```bash
python -m app.cli.main list-templates
python -m app.cli.main render-template --input /path/to/resume.json --template-key ats-markdown-starter
```

## Automation Preferences and State Machine

ApplyForge implements a portable user preference profile and a formal application run state machine:
*   **Preferences**: Combine canonical profile data, saved answers, target roles, filters, and resume defaults. Accessible via `/settings` and exportable (`GET /profile/preferences/export`).
*   **State Machine**: Governs application runs with explicit transitions (`queued`, `running`, `paused`, `failed`, `completed`, `uncertain`).

## Documentation Directory

Explore the `docs` folder for detailed information:
*   `docs/LOCAL_DOCKER.md`: Docker startup, seeding, and troubleshooting.
*   `docs/DEPLOYMENT.md`: Deployment topology, configuration, and caveats.
*   `docs/REQUIREMENTS.md`: Product requirements and system invariants.
*   `docs/ARCHITECTURE.md`: Runtime and data-flow architecture.
*   `docs/CONTEXT.md`: Quick orientation guide for developers.
*   `docs/TODO.md`: Remaining hardening tasks and future work.
*   `docs/FEATURE_REQUESTS/applypilot-core-roadmap.md`: Roadmap status.
*   `docs/IDEAS/company-intelligence-directory.md`: Company directory foundation status.

## Development Commands

Use the provided Makefile for common tasks:

```bash
make api
make web
make worker
make api-test
make web-typecheck
make lint
```

## Core Safety Rules

*   **Fact Preservation**: Resume tailoring never invents facts; it only preserves and reformats existing, verified information.
*   **Candidate Review**: Unknown application questions default to "Requires candidate review".
*   **Risk Mitigation**: Sensitive or risky prompts (e.g., salary, visa status) mandate manual user approval.
*   **Auditability**: All automation runs persist detailed step logs, retry counts, timestamps, and structured outputs for review.

## Current Limitations

*   Full Alembic migration history is scaffolded but requires further authoring.
*   Job enrichment relies on worker queues, but detailed retry/backoff observability is limited.
*   Frontend document editing is functional but would benefit from advanced section editors.
*   Enterprise features (multi-user, agency workflows, S3 storage) are slated for future development.
