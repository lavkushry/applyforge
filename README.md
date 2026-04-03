# ApplyForge: AI-Powered Job Hunt OS

ApplyForge is a comprehensive, production-ready MVP monorepo designed to streamline and automate your entire job search process. It seamlessly integrates intelligent resume parsing, role-based job discovery, fit analysis, custom document generation, and a secure, browser-assisted application executor into a unified platform.

## Architecture Overview

- `apps/web`: The frontend interface built with Next.js and TypeScript. It includes the dashboard, profile management, job tracking, and diagnostics views.
- `apps/api`: The backend service powered by FastAPI and SQLAlchemy, handling authentication, resume processing, job matching, tailoring, file management, and workflow orchestration.
- `apps/worker`: A robust Celery and Playwright-based execution engine that handles step-by-step application automation, capturing necessary screenshots, and enforcing pause checks.
- `packages/prompts`: A collection of templates used for cleaning resumes, normalizing job descriptions, computing fit scores, generating cover letters, predicting answers, and assessing application risks.
- `infra`: Infrastructure configurations including Docker Compose setups and Dockerfiles for seamless local development.
- `docs`: A comprehensive library of architectural decisions, deployment guides, and future feature plans.
- `.codex` and `.agents`: Configuration files defining agent roles and capabilities for AI-driven project maintenance.

## Supported Features

### Phase 1: Core Fundamentals
- Standard email/password authentication using secure, cookie-based sessions.
- Full CRUD operations for candidate profiles, paired with a robust resume upload and text extraction pipeline.
- Manual job entry with built-in normalization and deduplication logic.
- Scheduled role scraping that discovers jobs and queues them for automated enrichment.
- A built-in registry of discovery presets, providing out-of-the-box templates for common job boards and ATS platforms (e.g., Workday).
- An intelligent job scoring system that provides clear fit explanations, tracks enrichment updates, and offers actionable recommendations.
- Core UI pages: Dashboard, Job Listings, Job Details, Resume Management, and Profile Settings.

### Phase 2: Document Generation
- Context-aware resume tailoring that dynamically highlights relevant experience without fabricating facts.
- High-quality, ATS-optimized PDF generation for various resume versions.
- A catalog of ready-to-use Markdown and LaTeX resume templates, supplemented by developer CLI tools.
- Automated cover letter drafting customized per job application.
- A Kanban-style application tracking board and extended settings panels.

### Phase 3: Application Automation
- A detailed, step-by-step application logging system that permanently records run statuses.
- Support for API-driven auto-apply flows and assisted execution modes, featuring mandatory review pauses before final submission.
- A dry-run capability (Draft Mode) for reviewing application packets before any browser interaction occurs.
- A headless Playwright worker that automates common form fields while generating visual evidence (screenshots) of the process.
- An interactive UI for reviewing the automation timeline, diagnosing failures, and managing pipeline stages.
- Event-driven feeds that track worker job enrichments and score adjustments over time.
- A guided setup wizard for new users, offering readiness evaluations and quick role configuration using provided templates.
- A robust Finite State Machine (FSM) tracking run transitions and the ability to export portable user preferences for offline use.

### Phase 4: Intelligence & Customization
- A user-specific directory for tracking company intelligence, career portal URLs, and recruiter contacts.
- An expanded resume template library integrated with standard Markdown and LaTeX toolchains.
- Exportable automation settings directly accessible from the user preferences dashboard.

## Repository Structure

```text
/apps
  /api       (FastAPI Backend)
  /web       (Next.js Frontend)
  /worker    (Celery + Playwright)
/packages
  /config    (Presets and Defaults)
  /prompts   (LLM Templates)
  /shared    (Shared Utilities)
  /types     (TypeScript Interfaces)
  /ui        (Shared UI Components)
/infra       (Docker Orchestration)
/docs        (Documentation)
/.codex      (Agent Configurations)
/.agents     (Project Skills)
```

## Getting Started

### 1. System Requirements

- Docker Engine and Docker Compose
- Node.js (v20 or newer)
- Python (v3.12 or newer)

### 2. Environment Configuration

Copy the example environment files to their respective locations:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Running with Docker (Recommended)

Boot up the entire stack using Docker Compose:

```bash
cd infra
docker compose up --build
```

Access the services via:

- **Web Application**: `http://localhost:3000`
- **API Swagger Docs**: `http://localhost:8000/docs`
- **Celery Monitor (Flower)**: `http://localhost:5555`

### 4. Running Locally (Without Docker)

Install dependencies and start the development servers:

```bash
make setup
make dev
```

In a new terminal window, populate the database with initial test data:

```bash
make seed
```

You can now log in using the default local credentials:

- **Email**: `defaultuser@applyforge.dev`
- **Password**: `defaultuser123`

## Built-In Discovery & Bootstrapping

ApplyForge includes a curated configuration registry (inspired by ApplyPilot) to jumpstart your job search:

- `packages/config/discovery/employers.yaml`
- `packages/config/discovery/sites.yaml`
- `packages/config/discovery/searches.example.yaml`

These configurations drive the underlying setup API:
- `GET /roles/source-presets`
- `GET /setup/wizard`
- `POST /setup/wizard/bootstrap-role`

Through the `/wizard` and `/roles` pages, users can effortlessly initialize search parameters and attach robust source presets (including complex ATS targets) without writing custom configuration code.

## OAuth Integration for Inbox Access

ApplyForge supports connecting external email accounts (Gmail or Outlook) to automatically retrieve OTPs (One-Time Passwords) during application runs.

Ensure the following variables are populated in `apps/api/.env`:

- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_REDIRECT_URI`
- `MICROSOFT_OAUTH_CLIENT_ID`
- `MICROSOFT_OAUTH_CLIENT_SECRET`
- `MICROSOFT_OAUTH_TENANT`
- `MICROSOFT_OAUTH_REDIRECT_URI`

**Local Testing URIs:**
- Google: `http://localhost:8000/inbox/gmail/oauth/callback`
- Microsoft: `http://localhost:8000/inbox/outlook/oauth/callback`

Once configured, users can authorize inbox access directly from the web application's Settings page, which also actively monitors provider readiness.

## Resume Styling & Export

Drawing inspiration from structured resume frameworks, ApplyForge includes a robust template system:

- `packages/config/resume/sections.json`
- `packages/config/resume/resume_template.md`
- `packages/config/resume/resume_template.tex`

These assets support web previews (`/resume`) and developer CLI interactions:
```bash
python -m app.cli.main list-templates
python -m app.cli.main render-template --input /path/to/resume.json --template-key ats-markdown-starter
```
The PDF rendering pipeline primarily utilizes RenderCV, with a reliable internal fallback mechanism ensuring high availability.

## State Management & Portable Preferences

ApplyForge maintains a strict Finite State Machine for application tracking (`queued`, `running`, `paused`, `failed`, `completed`, `uncertain`) and supports exporting complete user configuration profiles.

These comprehensive exports bundle canonical profile details, job matching rules, answer histories, and automation settings into easily portable JSON or text formats.

## Further Reading

Explore the documentation directory for deeper insights:

- [Local Docker Guide](docs/LOCAL_DOCKER.md): Detailed startup instructions and troubleshooting for local containerized environments.
- [Deployment Strategy](docs/DEPLOYMENT.md): Topology overview, security considerations, and production deployment checklists.
- [Product Requirements](docs/REQUIREMENTS.md): Core specifications, product boundaries, and invariant rules.
- [Architecture Details](docs/ARCHITECTURE.md): In-depth examination of system boundaries and data flows.
- [Context Overview](docs/CONTEXT.md): A rapid onboarding guide for future code contributions.
- [TODOs & Roadmap](docs/TODO.md): Pending tasks and planned feature expansions.

## Helpful Makefile Commands

```bash
make api             # Start the backend server
make web             # Start the frontend dev server
make worker          # Start the Celery task consumer
make api-test        # Execute the Python test suite
make web-typecheck   # Verify TypeScript definitions
make lint            # Run frontend linters
```

## System Guardrails

- **Factual Integrity**: Automated tailoring never hallucinates experience or alters facts from the canonical profile.
- **Graceful Degradation**: Unrecognized form fields immediately trigger a manual review request.
- **Risk Mitigation**: Applications requesting sensitive data (e.g., compensation expectations, visa status) pause automatically for human intervention.
- **Full Auditability**: Every automated action generates timestamps, execution logs, and detailed artifact trails.

## Known Limitations & Next Steps

- **Database Migrations**: Alembic revision scripts require further authoring to completely replace the current `create_all` local startup logic.
- **Worker Observability**: Retry visibility and backoff monitoring for backend job enrichments need UI enhancements.
- **Document Editing UX**: The current web profile editor is fully functional but will benefit from more advanced, rich-text section handling in future updates.
- **Enterprise Capabilities**: Multi-tenant isolation, agency features, and integration with S3-compatible blob storage remain under active development.
