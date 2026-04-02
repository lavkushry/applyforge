# ApplyForge

**Your AI-Powered Job Hunt Operating System**

ApplyForge is a comprehensive, production-minded MVP monorepo designed to streamline and automate end-to-end job search operations. It unifies resume intelligence, job discovery, fit scoring, tailored document generation, and guarded browser automation within a single cohesive product scaffold.

## Core Features and Implementation Status

The platform has been built across several key phases, introducing robust functionality at each step.

### Phase 1: Foundation and Discovery
- **Authentication:** Secure email/password login utilizing cookie-backed session tokens.
- **Candidate Intelligence:** Comprehensive profile management with automated resume upload and parsing capabilities.
- **Job Ingestion & Normalization:** Manual and automated role scraping with intelligent job discovery, duplicate detection, and worker-queued enrichment.
- **Discovery Presets:** Packaged configuration registry providing examples for search templates, direct-site integrations, and Workday-style source presets.
- **Transparent Scoring Engine:** Advanced job scoring with clear reasoning, enrichment revisions, and actionable recommendations.
- **User Interface:** Fully functional dashboard, jobs list, job detail views, resume management, and profile editing pages.

### Phase 2: Tailoring and Export
- **Dynamic Resume Generation:** Tailored resume creation enforcing strict factual constraints (fact-locked content reuse).
- **Professional Exports:** ATS-friendly PDF generation for various resume iterations.
- **Template System:** Packaged Markdown and LaTeX resume starter templates supported by developer CLI tools.
- **Cover Letters:** Automated, context-aware cover-letter generation.
- **Application Tracking:** Intuitive application tracker board and comprehensive settings management.

### Phase 3: Automation and Execution
- **Step-Based Application Runs:** Detailed application run records tracking persistent statuses across the application lifecycle.
- **Guarded Automation:** Assisted and auto-run API flows incorporating "pause-before-submit" safety mechanisms.
- **Pre-flight Checks:** Draft packet-review features allowing for dry-run preparations before actual submission.
- **Playwright Worker Integration:** Robust worker skeleton handling automated field filling and capturing crucial screenshot evidence.
- **Run Diagnostics:** Visual run timelines and detailed diagnostic user interfaces.
- **Feed Events:** Worker-backed updates for job enrichment and score-change events.
- **Control Center:** Comprehensive application management interface providing pipeline-stage visibility and manual operator controls.
- **Setup Wizard:** Streamlined onboarding experience with readiness checks and one-click role bootstrapping using packaged templates.
- **Formal State Management:** Robust run-state transitions and reusable user-preference exports enabling advanced automation.

### Phase 4 Foundations: Enterprise Intelligence
- **Company Directory:** User-scoped company intelligence tracking, integrating portal data and recruiter contacts.
- **Advanced Resume Catalog:** Expanded resume template catalog and developer CLI aligned with structured Markdown and LaTeX workflows.
- **Portable Automation:** Exportable automation preference profiles accessible directly from user settings.

## System Architecture

ApplyForge utilizes a modern monorepo structure, separating concerns across distinct applications and packages.

- `apps/web`: A Next.js and TypeScript frontend application housing marketing pages, the user dashboard, profile editing, job discovery, the tracker, and diagnostic views.
- `apps/api`: A FastAPI and SQLAlchemy backend service handling authentication, profile and resume workflows, job normalization, scoring algorithms, document tailoring, file management, and application run states.
- `apps/worker`: A Celery and Playwright executor executing step-based, assisted-apply processes while capturing screenshots and managing pause gates.
- `packages/prompts`: Centralized prompt templates for resume processing, job normalization, scoring, tailoring, cover letter generation, question answering, and risk detection.
- `infra`: Docker Compose configurations and Dockerfiles enabling streamlined local orchestration.
- `docs`: Comprehensive architecture notes, TODO lists, and product operating documentation.
- `.codex` and `.agents`: Project-local agent role definitions and skills designed for future AI-assisted development and maintenance.

### Monorepo Structure

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

## Getting Started

### 1. Prerequisites

Ensure you have the following installed on your system:

- Docker and Docker Compose
- Node.js (v20 or higher)
- Python (v3.12 or higher)

### 2. Environment Configuration

Copy the example environment files to configure your local setup:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
cp apps/worker/.env.example apps/worker/.env
```

### 3. Launching with Docker

To start the complete application stack using Docker:

```bash
cd infra
docker compose up --build
```

**Available Services:**
- Web Interface: `http://localhost:3000`
- API Documentation: `http://localhost:8000/docs`
- Flower (Worker Dashboard): `http://localhost:5555`

### 4. Local Development (Without Docker)

For native local development, initialize and run the services using Make commands:

```bash
make setup
make dev
```

In a separate terminal session, seed the database with initial data:

```bash
make seed
```

**Default Local Credentials:**
- Email: `defaultuser@applyforge.dev`
- Password: `defaultuser123`

## Key Capabilities and Configurations

### Discovery Presets and Setup Wizard

ApplyForge includes a packaged discovery registry, inspired by ApplyPilot-style configurations, located in `packages/config/discovery/`.

These files (`employers.yaml`, `sites.yaml`, `searches.example.yaml`) power the discovery APIs (`/roles/source-presets`, `/setup/wizard`, `/setup/wizard/bootstrap-role`) and enable the web application's onboarding wizard. Users can easily attach packaged source presets, including complex Workday-style boards, directly from the `/roles` interface without manual configuration.

### Inbox OAuth Integration

To facilitate automated OTP email retrieval during application runs, ApplyForge supports connecting Gmail and Outlook accounts.

Configure the necessary API environment variables in `apps/api/.env`:

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

Ensure the required provider scopes (e.g., `gmail.readonly`, `Mail.Read`) are configured in your OAuth application. Once configured, users can connect their accounts via the Settings page, which also provides diagnostics on missing environment variables.

### Resume Template Catalog and CLI

ApplyForge provides a structured resume-template layer located in `packages/config/resume/` (including `sections.json`, `resume_template.md`, and `resume_template.tex`).

This system powers the template APIs and provides a CLI utility (`app.cli.main list-templates` and `render-template`). The web interface (`/resume`) allows users to browse and render Markdown and LaTeX starter templates using their canonical profile data. The primary PDF export utilizes a robust internal fallback pipeline, ensuring RenderCV compatibility.

### Automation Preferences and State Management

The platform includes portable user preferences and a formal application run state machine.

Exportable preferences (combining profile data, saved answers, target roles, filters, and resume defaults) are accessible via the `/settings` page and API endpoints. Application runs strictly adhere to transition rules defined in the State Machine (`queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`).

## Core Safety Rules

ApplyForge enforces strict operational guardrails:

- **Factual Integrity:** Resume tailoring processes never invent facts and strictly preserve fact-locked sections.
- **Unknown Information:** Unrecognized application questions default to requiring manual candidate review.
- **Risk Mitigation:** Risky or sensitive questions (e.g., salary, visa status) force mandatory manual approval.
- **Auditability:** All automation runs durably persist step logs, retry counts, execution timestamps, and structured outputs.

## Useful Development Commands

```bash
make api             # Start API service
make web             # Start Web service
make worker          # Start Celery worker
make api-test        # Run API test suite
make web-typecheck   # Run Web TypeScript checks
make lint            # Run codebase linters
```

## Documentation Directory

Explore the `docs/` folder for in-depth information:

- [LOCAL_DOCKER.md](./docs/LOCAL_DOCKER.md): Local Docker startup, seed flow, and troubleshooting.
- [DEPLOYMENT.md](./docs/DEPLOYMENT.md): Deployment topologies, environment setup, and rollout guidance.
- [REQUIREMENTS.md](./docs/REQUIREMENTS.md): Detailed product requirements and invariants.
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md): Comprehensive runtime and data-flow architecture.
- [CONTEXT.md](./docs/CONTEXT.md): Fast orientation guide for understanding the project.
- [TODO.md](./docs/TODO.md): Remaining technical hardening and future work.
- [FEATURE_REQUESTS/applypilot-core-roadmap.md](./docs/FEATURE_REQUESTS/applypilot-core-roadmap.md): Status of the core roadmap.
- [IDEAS/company-intelligence-directory.md](./docs/IDEAS/company-intelligence-directory.md): Foundation for the company directory feature.

## Current Gaps and Future Work

- **Migrations:** Full Alembic database revision history is scaffolded but requires comprehensive authoring.
- **Worker Observability:** Retry and backoff observability for queued job enrichment tasks requires improvement.
- **Document Editing:** The frontend document editor is currently MVP-grade and will benefit from advanced section-based editing.
- **Enterprise Features:** Multi-user support, agency workflows, and S3-compatible storage integration are slated for future phases.
