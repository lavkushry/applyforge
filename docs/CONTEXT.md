# ApplyForge Context Guide

This guide is intended to reduce the rediscovery cost for developers and operators in future sessions by providing a fast orientation to the ApplyForge system.

## System Identity

ApplyForge is a comprehensive job-hunt operating system built around five connected operational loops:

1.  **Canonical Profile & Resume Intelligence**: Maintaining a single source of truth for candidate skills and experience.
2.  **Role-Driven Discovery & Enrichment**: Automated sourcing and enrichment of job opportunities based on target roles.
3.  **Transparent Scoring & Tailoring**: Fact-based evaluation of job fit and automated, tailored document generation.
4.  **Guarded Application Execution**: Browser-assisted job applications with explicit checkpoints and evidence capture.
5.  **Diagnostics & Operator Review**: System observability, OTP integration, and manual oversight capabilities.

## Current Product Capabilities

The repository currently supports the following functional areas:

### Core Identity & Resumes
*   Cookie-backed authentication sessions.
*   Canonical candidate profile CRUD (Create, Read, Update, Delete) operations.
*   Automated resume upload, text extraction, and parsing.
*   A catalog of ATS-safe light themes for resume styling.
*   Packaged Markdown and LaTeX resume starter templates.
*   RenderCV-compatible input generation with an internal PDF rendering fallback.

### Job Discovery & Evaluation
*   Role registry management and source subscriptions.
*   Packaged discovery presets and a setup wizard for rapid bootstrapping.
*   Near-realtime job feeds powered by ingestion runs and state-change feed events.
*   A robust company directory tracking records, career portals, and recruiter contacts.
*   Explicit data pipelines: Discovery -> Enrichment -> Scoring.
*   Worker-queued job enrichment for deeper data extraction.
*   Transparent scoring engine with fact-locked resume tailoring.

### Automation & Execution
*   Preparation of structured application packets.
*   Durable application runs with comprehensive step logs.
*   Formal finite state machine (FSM) transitions for run states.
*   Gmail and Outlook OAuth integration readiness for OTP retrieval.
*   Exportable automation preference profiles accessible via User Settings.

## Core Invariants

These principles must be preserved in all future changes:

1.  **Authoritative Profile**: The canonical candidate profile is the ultimate source of truth for all facts.
2.  **Fact-Locked Generation**: Generated outputs (resumes, cover letters, answers) may optimize phrasing but **must never** fabricate facts or qualifications.
3.  **Role-Driven Policy**: Target role strategies dictate discovery and automation behaviors.
4.  **Presentation vs. Data**: Resume themes and starter templates act solely as presentation layers, not data sources.
5.  **Inspectable Automation**: Application automation must remain fully inspectable, leaving a durable audit trail even after partial failures.
6.  **Secure Operations**: Sensitive tokens, OTPs, and high-risk application answers must remain masked or require explicit user approval.

## Best Entry Points by Task

Use these starting files when working on specific domains:

### Resumes, Templates, and Export
*   `apps/api/app/services/resume_parser.py`
*   `apps/api/app/services/resume_themes.py`
*   `apps/api/app/services/resume_templates.py`
*   `apps/api/app/services/files.py`
*   `apps/web/app/resume/page.tsx`

### Jobs, Roles, and Scoring
*   `apps/api/app/services/role_ingestion.py`
*   `apps/api/app/services/job_dispatch.py`
*   `apps/api/app/services/job_enrichment.py`
*   `apps/api/app/services/company_directory.py`
*   `apps/api/app/services/scoring.py`
*   `apps/api/app/api/routes/roles.py`
*   `apps/api/app/api/routes/jobs.py`
*   `apps/api/app/api/routes/companies.py`

### Automation, Packets, and FSM
*   `apps/api/app/api/routes/applications.py`
*   `apps/api/app/api/routes/application_runs.py`
*   `apps/api/app/services/application_packets.py`
*   `apps/api/app/services/application_fsm.py`
*   `apps/api/app/services/user_preferences.py`
*   `apps/worker/app/playwright_runner.py`
*   `apps/worker/app/persistence.py`
*   `apps/worker/app/run_fsm.py`

### Settings, OTP, and Operator UX
*   `apps/web/components/forms/settings-form.tsx`
*   `apps/api/app/services/inbox.py`
*   `apps/api/app/api/routes/inbox.py`
*   `apps/web/app/applications/page.tsx`
*   `apps/web/app/runs/[id]/page.tsx`

## Project-Local Context Helpers

Consult the project-local skill and agent files before embarking on broad exploration:
*   **Product/Domain Guidance**: `.agents/skills/applyforge-product/SKILL.md`
*   **Operations Guidance**: `.agents/skills/applyforge-ops/SKILL.md`
*   **Codex Agent Registry**: `.codex/config.toml`

## Current Verification Baseline

When submitting nontrivial changes, verify against the following baseline checks:

1.  **Compile Python Files**:
    `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2.  **API Tests**:
    `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3.  **Worker Tests**:
    `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4.  **Web Linter**:
    `npm run lint` (run inside `apps/web`)
5.  **Web Build**:
    `npm run build` (run inside `apps/web`)
6.  **Web Typecheck**:
    `npm run typecheck` (run inside `apps/web`)

*Note: In this repository, `typecheck` is safest when executed after `build` because `tsconfig.json` includes `.next/types`.*

## Current Reality Checks

*   **Worker Capability**: The worker path is active for enrichment and application execution but remains at an MVP level regarding extensive field mapping coverage.
*   **Resume Export**: Continuity of resume export is prioritized over rendering purity; a RenderCV failure must gracefully fallback and not break the export process.
*   **OAuth Readiness**: OAuth code paths are implemented, but real-world provider credentials still require comprehensive live verification.
*   **Documentation Discipline**: Documentation should strictly describe current, implemented behavior, not future promises.
