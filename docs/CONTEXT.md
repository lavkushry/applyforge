# ApplyForge Orientation Guide

This document provides foundational context to help engineers quickly navigate and understand the ApplyForge codebase.

## ApplyForge Overview

ApplyForge is a comprehensive operating system designed to streamline the job search process. It orchestrates five interconnected workflows:

1. Centralized candidate profile and resume data parsing.
2. Targeted job discovery and data enrichment based on specific roles.
3. Algorithmic scoring and automated resume tailoring.
4. Secure, browser-driven automation for submitting applications.
5. Operational monitoring, including diagnostic tools, OTP handling, and manual review checkpoints.

## Supported Capabilities

The current repository implements a robust set of features, including:

- Secure, cookie-based user authentication.
- Full CRUD operations for canonical candidate profiles.
- Automated ingestion and parsing of uploaded resumes.
- A library of ATS-optimized light themes.
- Out-of-the-box Markdown and LaTeX starter templates.
- PDF generation leveraging RenderCV with a reliable internal fallback mechanism.
- A central registry for job roles and automated source subscriptions.
- Pre-configured discovery setups and a guided onboarding wizard.
- A near-realtime job feed powered by background ingestion processes.
- An integrated company directory mapping portals and recruiter contacts.
- A structured pipeline moving jobs from discovery through enrichment to scoring.
- Background task queues handling job enrichment via asynchronous workers.
- Transparent match scoring and strict, fact-based resume tailoring.
- Compilation of complete, structured application packets.
- Durable logging of application runs and individual execution steps.
- Strict finite-state machine (FSM) control over application statuses.
- Infrastructure supporting Gmail and Outlook OAuth for OTP retrieval.
- Exportable automation preference profiles accessible via the user settings.

## Core Directives

When modifying the system, strictly adhere to these invariants:

1. **Profile Authority:** The user's canonical profile is the definitive source of truth.
2. **Fact Fidelity:** The system may optimize language during tailoring, but it must never fabricate information.
3. **Role-Driven Logic:** The user's target role strategy dictates the rules for both discovery and automation.
4. **Theme Boundaries:** Resume themes and templates are strictly for presentation; they do not alter underlying profile facts.
5. **Automation Transparency:** If an automation run fails, the system must retain sufficient logs and evidence for inspection.
6. **Data Security:** Sensitive information, such as OAuth tokens, OTP codes, and high-risk application answers, must remain securely masked or require explicit user approval.

## Code Navigation Guide

### Resume processing, templates, and document generation

- [resume_parser.py](../apps/api/app/services/resume_parser.py)
- [resume_themes.py](../apps/api/app/services/resume_themes.py)
- [resume_templates.py](../apps/api/app/services/resume_templates.py)
- [files.py](../apps/api/app/services/files.py)
- [resume/page.tsx](../apps/web/app/resume/page.tsx)

### Job ingestion, roles, and match scoring

- [role_ingestion.py](../apps/api/app/services/role_ingestion.py)
- [job_dispatch.py](../apps/api/app/services/job_dispatch.py)
- [job_enrichment.py](../apps/api/app/services/job_enrichment.py)
- [company_directory.py](../apps/api/app/services/company_directory.py)
- [scoring.py](../apps/api/app/services/scoring.py)
- [roles.py](../apps/api/app/api/routes/roles.py)
- [jobs.py](../apps/api/app/api/routes/jobs.py)
- [companies.py](../apps/api/app/api/routes/companies.py)

### Automated applications, execution packets, and state machines

- [applications.py](../apps/api/app/api/routes/applications.py)
- [application_runs.py](../apps/api/app/api/routes/application_runs.py)
- [application_packets.py](../apps/api/app/services/application_packets.py)
- [application_fsm.py](../apps/api/app/services/application_fsm.py)
- [user_preferences.py](../apps/api/app/services/user_preferences.py)
- [playwright_runner.py](../apps/worker/app/playwright_runner.py)
- [persistence.py](../apps/worker/app/persistence.py)
- [run_fsm.py](../apps/worker/app/run_fsm.py)

### Operator interfaces, settings, and inbox handling

- [settings-form.tsx](../apps/web/components/forms/settings-form.tsx)
- [inbox.py](../apps/api/app/services/inbox.py)
- [inbox.py](../apps/api/app/api/routes/inbox.py)
- [applications/page.tsx](../apps/web/app/applications/page.tsx)
- [runs/[id]/page.tsx](../apps/web/app/runs/[id]/page.tsx)

## Local Development Aids

Consult these files to understand the project's specific domain context and operational guidelines before undertaking major changes:

- Domain rules: [SKILL.md](../.agents/skills/applyforge-product/SKILL.md)
- Operational rules: [SKILL.md](../.agents/skills/applyforge-ops/SKILL.md)
- AI Agent definitions: [config.toml](../.codex/config.toml)

## Pre-Commit Verification

Always run these verification steps to ensure system stability before submitting complex changes:

1. `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. Execute `npm run lint` within the `apps/web` directory.
5. Execute `npm run build` within the `apps/web` directory.
6. Execute `npm run typecheck` within the `apps/web` directory.

*Note: In this project structure, it is highly recommended to run `typecheck` only after `build` since the `tsconfig.json` configuration relies on compiled `.next/types`.*

## Important Contextual Realities

- The worker architecture actively handles job enrichment and application submissions, though its test coverage in real-world scenarios is currently at an MVP stage.
- Generating a usable exported resume is paramount; if RenderCV processing encounters an error, the system must gracefully fall back rather than breaking the export entirely.
- The framework for OAuth integrations is fully implemented in the code, but it requires validation against live provider credentials.
- All documentation should strictly reflect the system's current state and capabilities, rather than outlining unbuilt features. Maintain this descriptive discipline.
