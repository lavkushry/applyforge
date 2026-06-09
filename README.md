# ApplyForge

**The AI-Powered Operating System for Your Job Search**

ApplyForge is a comprehensive, production-ready monorepo designed to manage the entire job hunting lifecycle. It integrates intelligent resume parsing, role-based job discovery, sophisticated fit scoring, automated document tailoring, and secure, browser-driven application submission into a unified platform.

## System Architecture

The project is structured as a monorepo containing the following core domains:

- `apps/web`: A Next.js (TypeScript) frontend providing the user interface for marketing, dashboards, profile management, job tracking, and system diagnostics.
- `apps/api`: A FastAPI (Python) backend utilizing SQLAlchemy for data persistence. It handles authentication, profile/resume logic, job normalization, scoring, document tailoring, and application state management.
- `apps/worker`: A Celery-based asynchronous executor utilizing Playwright to perform automated application steps, capturing screenshots and handling necessary pause gates.
- `packages/prompts`: A collection of standardized prompts used for interacting with language models for resume parsing, scoring, and cover letter generation.
- `infra`: Docker configurations tailored for local development orchestration.
- `docs`: Extensive documentation covering architecture, requirements, and future roadmaps.
- `.codex` & `.agents`: Configuration files defining agent roles and rules for AI-assisted development.

## Implementation Milestones

### Core Foundations (Phase 1)
- User authentication via cookie-backed sessions.
- Comprehensive CRUD interfaces for the canonical candidate profile, including resume upload and text extraction.
- Manual job entry with duplicate detection.
- Automated job discovery pipelines based on defined roles, queuing jobs for deeper enrichment.
- A library of predefined discovery configurations, including direct-site setups and ATS-specific (e.g., Workday) templates.
- An intelligent scoring engine providing transparent feedback, including strengths, gaps, and recommendations.
- Core UI components: Dashboard, Job Listings, Resume Management, and Profile Editor.

### Document Generation (Phase 2)
- Dynamic resume tailoring that strictly relies on existing profile facts without fabrication.
- High-quality, ATS-optimized PDF generation.
- Provision of Markdown and LaTeX starter templates, supported by developer CLI tools.
- Automated generation of context-aware cover letters.
- A Kanban-style application tracking board.

### Automation & Orchestration (Phase 3)
- Detailed logging of application execution steps with durable status persistence.
- Support for API-driven automated runs, featuring safe "pause-before-submit" checkpoints.
- "Draft runs" allowing users to review prepared application packets before execution.
- A robust Playwright worker capable of navigating forms, filling fields, and capturing visual evidence.
- An administrative control center for monitoring pipelines and executing manual interventions.
- A guided setup wizard to quickly bootstrap user roles from predefined templates.
- A strict Finite State Machine (FSM) governing application lifecycles and exportable user preference profiles.

### Advanced Capabilities (Phase 4 - In Progress)
- A user-specific Company Intelligence Directory linking jobs to specific organizations, portals, and contacts.
- A comprehensive resume template catalog aligning with structured Markdown/LaTeX outputs.
- Portable configurations allowing users to easily export their automation settings.

## Getting Started

### 1. Prerequisites
Ensure you have the following installed:
- Docker and Docker Compose
- Node.js (version 20 or higher)
- Python (version 3.12 or higher)

### 2. Environment Configuration
Duplicate the example environment files:
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```
*(Note: Review these files and populate necessary secrets, such as API keys.)*

### 3. Launching via Docker
Initialize the stack using Docker Compose:
```bash
cd infra
docker compose up --build
```
Access the services at:
- Frontend: `http://localhost:3000`
- API Swagger Docs: `http://localhost:8000/docs`
- Celery Monitor (Flower): `http://localhost:5555`

### 4. Running Natively (Without Docker)
From the repository root:
```bash
make setup
make dev
```
In a separate terminal window, populate the database with initial test data:
```bash
make seed
```
You can then log in using the default credentials:
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

## Packaged Configurations & Onboarding

ApplyForge includes pre-built configurations to accelerate setup:
- Source definitions: `packages/config/discovery/employers.yaml`, `sites.yaml`, `searches.example.yaml`
- Resume templates: `packages/config/resume/sections.json`, `resume_template.md`, `resume_template.tex`

These power the `/wizard` onboarding flow and allow users to instantly attach robust discovery configurations (like Workday scrapers) via the `/roles` UI.

## OAuth Integration for Inbox OTPs

ApplyForge can securely connect to Gmail or Outlook to automatically fetch One-Time Passwords (OTPs) during application runs.

To enable this, configure the following variables in `apps/api/.env`:
- Google: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`
- Microsoft: `MICROSOFT_OAUTH_CLIENT_ID`, `MICROSOFT_OAUTH_CLIENT_SECRET`, `MICROSOFT_OAUTH_TENANT`, `MICROSOFT_OAUTH_REDIRECT_URI`

*For local testing, use URLs like `http://localhost:8000/inbox/gmail/oauth/callback`.*
Once configured, users can connect their accounts via the Settings page.

## Automation States & Preferences

ApplyForge utilizes a formal Finite State Machine (FSM) to manage application attempts (`queued`, `running`, `paused`, `failed`, `completed`, `uncertain`).
Users can view and export their comprehensive automation profile (combining facts, filters, and preferences) directly from the `/settings` page.

## Documentation Library

For deeper dives into the system, consult the following guides:
- [Local Docker Guide](docs/LOCAL_DOCKER.md): Detailed local setup and troubleshooting.
- [Deployment Guide](docs/DEPLOYMENT.md): Instructions for staging and production environments.
- [Product Requirements](docs/REQUIREMENTS.md): Core invariants and expected behaviors.
- [Architecture](docs/ARCHITECTURE.md): System components and data flow.
- [Context Guide](docs/CONTEXT.md): Quick orientation for new contributors.
- [Roadmap & Status](docs/FEATURE_REQUESTS/applypilot-core-roadmap.md): Progress against the original vision.
- [Action Items](docs/TODO.md): Remaining engineering tasks.

## Frequently Used Commands

Run these from the repository root:
```bash
make api             # Start the backend server
make web             # Start the frontend dev server
make worker          # Start the Celery worker
make api-test        # Execute backend tests
make web-typecheck   # Verify frontend TypeScript types
make lint            # Run code linters
```

## Immutable Safety Principles

- **No Fabrication:** Tailoring processes must never invent experience or skills.
- **Human Oversight:** Ambiguous or high-risk application questions require explicit user review.
- **Traceability:** Every automated action must log its steps, retries, and outputs for auditing.

## Current Limitations

- Database schema changes currently rely on startup initialization rather than full Alembic migrations.
- While jobs are queued for enrichment, detailed observability for retry logic is limited in the UI.
- The web-based profile editor is functional but lacks advanced rich-text capabilities.
- True multi-tenant enterprise features and S3 object storage integration are planned for future phases.
