# ApplyForge: AI Job Search Operating System

Welcome to ApplyForge, an advanced, production-ready monorepo designed to manage and automate your job search end-to-end. ApplyForge provides a comprehensive suite of tools, from resume parsing and intelligent job discovery to tailored application generation and guided browser automation.

## System Architecture Overview

ApplyForge is structured as a monorepo containing several integrated applications and packages:

- **`apps/web`**: A modern Next.js and TypeScript frontend application providing user interfaces for dashboard monitoring, profile management, job tracking, and application workflows.
- **`apps/api`**: A high-performance FastAPI and SQLAlchemy backend handling core business logic, including authentication, document processing, job scoring, and application state management.
- **`apps/worker`**: A Celery-based background task processor paired with Playwright, responsible for executing complex, multi-step job application automation flows.
- **`packages/prompts`**: A collection of reusable prompt templates to drive the LLM logic used for resume tailoring, cover letter drafting, and job normalization.
- **`infra`**: Infrastructure configurations, including Dockerfiles and Compose files, to facilitate local development and deployment.
- **`docs`**: Comprehensive documentation covering system architecture, deployment procedures, and future roadmaps.
- **`.codex` & `.agents`**: Specialized configurations for AI agents to support ongoing maintenance and operational tasks.

## Feature Implementation Status

### Core Features (Phase 1)
- Robust email/password authentication using secure, HTTP-only cookies.
- Comprehensive candidate profile management with integrated resume upload and intelligent parsing.
- Seamless manual job ingestion combined with automated normalization and deduplication.
- Configurable discovery presets allowing tailored searches across multiple job boards.
- Transparent job scoring system that evaluates candidate fit and provides actionable recommendations.
- Interactive user interfaces for dashboards, job listings, detailed job views, and profile management.

### Advanced Generation (Phase 2)
- Dynamic resume tailoring that emphasizes relevant skills without fabricating facts.
- Reliable ATS-friendly PDF export for all customized resume versions.
- Built-in support for multiple resume formats, including structured Markdown and LaTeX starter templates.
- Automated cover letter drafting aligned with job requirements.
- Centralized tracking board for managing applications and system settings.

### Automation & Intelligence (Phase 3)
- Detailed application run tracking with durable state persistence.
- Configurable application execution modes (assisted vs. auto-run) with mandatory review checkpoints.
- Sophisticated Playwright worker capable of navigating complex application forms and capturing visual diagnostics.
- Event-driven job enrichment processes and realtime score updates.
- Centralized control center providing deep visibility into application pipeline stages.
- An intuitive setup wizard to rapidly configure roles based on packaged templates.

### Platform Foundations (Phase 4)
- A comprehensive directory mapping companies to their application portals and key contacts.
- A streamlined resume template catalog equipped with developer tools for Markdown and LaTeX workflows.
- Portable automation preference profiles, allowing users to export their settings for external integrations.

## Repository Structure

```text
/apps
  /api          # Backend services
  /web          # Frontend application
  /worker       # Background task processor
/packages
  /config       # Shared system configurations
  /prompts      # LLM prompt templates
  /shared       # Shared utilities
  /types        # TypeScript type definitions
  /ui           # Reusable UI components
/infra          # Deployment configurations
/docs           # System documentation
/.codex         # Codex agent configurations
/.agents        # specialized operational skills
```

## Getting Started

### 1. System Requirements

Ensure your environment meets the following prerequisites:
- Docker and Docker Compose
- Node.js version 20 or higher
- Python version 3.12 or higher

### 2. Environment Configuration

Initialize your environment variables by copying the provided examples:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Running with Docker (Recommended)

To start the entire ApplyForge stack using Docker Compose:

```bash
cd infra
docker compose up --build
```

Access the services at the following endpoints:
- **Web App**: `http://localhost:3000`
- **API Documentation**: `http://localhost:8000/docs`
- **Worker Monitor (Flower)**: `http://localhost:5555`

### 4. Running Locally (Without Docker)

For local development without Docker, use the provided Make commands:

```bash
make setup
make dev
```

In a new terminal session, populate the database with initial seed data:

```bash
make seed
```

**Default Test Credentials:**
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

## Packaged Presets & Setup Wizard

ApplyForge includes a sophisticated discovery registry, facilitating rapid setup through pre-configured templates.

Key configuration files:
- `packages/config/discovery/employers.yaml`
- `packages/config/discovery/sites.yaml`
- `packages/config/discovery/searches.example.yaml`

These configurations support the setup wizard accessible at `/wizard`, allowing users to quickly initialize their job search profiles and attach targeted source presets (e.g., Workday boards) directly from the `/roles` interface.

## Integrating Inbox OAuth

To enable ApplyForge to automatically retrieve OTPs from your email, configure OAuth integration for Gmail or Outlook.

Update `apps/api/.env` with your credentials:
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

**Required Scopes:**
- **Gmail**: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`
- **Outlook**: `openid`, `profile`, `email`, `offline_access`, `https://graph.microsoft.com/User.Read`, `https://graph.microsoft.com/Mail.Read`

Once configured, use the Settings page in the web application to authorize the connection.

## Resume Catalog & Export System

ApplyForge features a flexible resume template system supporting multiple formats.

Configuration locations:
- `packages/config/resume/sections.json`
- `packages/config/resume/resume_template.md`
- `packages/config/resume/resume_template.tex`

Users can browse and render these templates via the `/resume` web interface. Developers can also interact with the system using the built-in CLI:

```bash
python -m app.cli.main list-templates
python -m app.cli.main render-template --input /path/to/resume.json --template-key ats-markdown-starter
```

## Advanced Automation Settings

ApplyForge introduces robust application run states and portable automation preferences.

Users can manage their automation profiles, keyword filters, and resume defaults directly from the `/settings` page. Application workflows adhere to a strict state machine, transitioning through defined states such as `queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`.

## Explore the Documentation

For deeper insights, consult the detailed documentation files:

- [docs/LOCAL_DOCKER.md](docs/LOCAL_DOCKER.md): Local Docker environment setup and troubleshooting.
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md): Deployment architecture and environment guidelines.
- [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md): Product requirements and core system invariants.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Runtime flow and data architecture details.
- [docs/CONTEXT.md](docs/CONTEXT.md): Quick orientation guide for development.
- [docs/TODO.md](docs/TODO.md): Upcoming features and technical debt tracking.
- [docs/FEATURE_REQUESTS/applypilot-core-roadmap.md](docs/FEATURE_REQUESTS/applypilot-core-roadmap.md): Roadmap aligned with the ApplyPilot feature set.
- [docs/IDEAS/company-intelligence-directory.md](docs/IDEAS/company-intelligence-directory.md): Plans for the company directory component.

## Helpful Development Commands

```bash
make api
make web
make worker
make api-test
make web-typecheck
make lint
```

## System Safety Principles

- **Data Integrity**: Resume tailoring optimizes language but never introduces false information.
- **User Control**: Any unrecognized application prompts automatically trigger a manual review request.
- **Risk Mitigation**: Sensitive questions regarding salary expectations or visa status require explicit user approval.
- **Traceability**: All automated actions maintain detailed step logs, timestamps, and structured outcome records.

## Known Limitations & Future Work

- Database schema evolution using Alembic is configured but requires ongoing authoring.
- Job enrichment observability features need enhancement to better monitor worker retries and backoffs.
- The web-based document editor currently provides basic functionality and is slated for an upgrade to support richer interactions.
- Future phases will introduce multi-user enterprise support, agency collaboration features, and robust cloud storage integrations like S3.

For a comprehensive overview of the system's current state and future direction, please review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/TODO.md](docs/TODO.md).
