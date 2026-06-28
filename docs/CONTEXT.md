# ApplyForge Developer Context Guide

This document is intended to accelerate orientation and reduce discovery time for engineers working within the ApplyForge monorepo.

## System Overview

ApplyForge operates as a comprehensive job-hunting ecosystem, structured around five distinct operational loops:

1. **Profile Management**: Maintaining a canonical candidate profile and processing resume data.
2. **Job Discovery**: Identifying and enriching job opportunities based on defined target roles.
3. **Scoring & Tailoring**: Evaluating job fit transparently and generating customized application materials.
4. **Execution Engine**: Managing browser-assisted application submissions with robust state tracking.
5. **Operator Oversight**: Providing diagnostic tools, OTP management, and manual review capabilities.

## Current Technical Capabilities

The ApplyForge repository currently supports the following features:

- Secure, cookie-based authentication.
- Complete CRUD operations for the canonical candidate profile.
- Automated resume parsing and data extraction.
- A catalog of ATS-friendly, light-themed resume designs.
- Starter templates for both Markdown and LaTeX resume formats.
- PDF generation compatible with RenderCV, backed by an internal rendering fallback.
- A registry for managing target roles and source subscriptions.
- Pre-packaged discovery presets and an interactive setup wizard for quick onboarding.
- A near-realtime feed displaying job ingestion and enrichment events.
- An intelligence directory for companies, tracking application portals and recruiter contacts.
- A defined pipeline transitioning jobs through discovery, enrichment, and scoring.
- Celery-worker queued processing for job enrichment tasks.
- A transparent scoring mechanism paired with fact-locked resume tailoring.
- Generation of fully prepared application packets.
- Durable tracking of application runs, complete with detailed step logs.
- Strict Finite State Machine (FSM) control over application execution phases.
- OAuth integration readiness for Gmail and Outlook to support automated OTP retrieval.
- Exportable automation preference profiles managed via the Settings interface.

## Core Architectural Invariants

Engineers must adhere to the following invariants when modifying the system:

1. **Source of Truth**: The canonical profile is the absolute source of truth for candidate data.
2. **Fact Preservation**: Generative features (like resume tailoring) are strictly prohibited from fabricating information; they may only optimize the presentation of existing facts.
3. **Role-Driven Actions**: The configured role strategy dictates all job discovery and automation policies.
4. **Presentation Separation**: Resume themes and starter templates operate purely as presentation layers, not data stores.
5. **Inspectability**: The application execution engine must provide detailed, inspectable logs, especially following a partial failure.
6. **Security & Privacy**: Sensitive data (e.g., OTPs, tokens) and high-risk application answers must remain masked or require explicit user approval before submission.

## Key Component Entry Points

When addressing specific functional areas, refer to the following critical files:

### Resumes, Templates, and Document Generation

- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`
- `apps/api/app/services/files.py`
- `apps/web/app/resume/page.tsx`

### Job Processing, Roles, and Scoring Logic

- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/company_directory.py`
- `apps/api/app/services/scoring.py`
- `apps/api/app/api/routes/roles.py`
- `apps/api/app/api/routes/jobs.py`
- `apps/api/app/api/routes/companies.py`

### Automation Workflows, Packets, and the FSM

- `apps/api/app/api/routes/applications.py`
- `apps/api/app/api/routes/application_runs.py`
- `apps/api/app/services/application_packets.py`
- `apps/api/app/services/application_fsm.py`
- `apps/api/app/services/user_preferences.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/persistence.py`
- `apps/worker/app/run_fsm.py`

### User Settings, OTP Handling, and Operator Interface

- `apps/web/components/forms/settings-form.tsx`
- `apps/api/app/services/inbox.py`
- `apps/api/app/api/routes/inbox.py`
- `apps/web/app/applications/page.tsx`
- `apps/web/app/runs/[id]/page.tsx`

## Utilizing Local Context Agents

Before embarking on broad exploratory tasks, consult the project-specific agent guidance files:

- Product and domain strategy: `.agents/skills/applyforge-product/SKILL.md`
- Operational guidelines: `.agents/skills/applyforge-ops/SKILL.md`
- Codex agent configuration: `.codex/config.toml`

## Mandatory Verification Baselines

All substantial modifications must pass the following baseline checks:

1. Validate Python compilation: `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. Execute API unit tests: `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. Execute Worker unit tests (using in-memory DB and local Redis): `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. Lint Next.js code: `npm run lint` within `apps/web`
5. Build Next.js app: `npm run build` within `apps/web`
6. Verify TypeScript types: `npm run typecheck` within `apps/web`

*Note: It is recommended to run `typecheck` after `build` in the `apps/web` directory, as the `tsconfig.json` relies on generated types in `.next/types`.*

## Important Operational Realities

- The Celery worker handles critical paths for job enrichment and application automation, but test coverage for edge cases in the field remains an ongoing MVP effort.
- The reliability of the resume export process takes precedence over renderer purity. If RenderCV fails, the system must gracefully degrade without breaking the core export function.
- While OAuth integration code exists, comprehensive end-to-end verification with live provider credentials is required.
- **Documentation Policy**: Documentation must accurately reflect the system's *current* operational state, not aspirational future goals. Maintain this discipline diligently.
