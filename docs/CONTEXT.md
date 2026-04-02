# ApplyForge Context Guide

*This document serves as a rapid orientation guide for developers, designed to minimize rediscovery time during future development sessions.*

## What Is ApplyForge?

ApplyForge is a comprehensive job-hunt operating system built around five interconnected functional loops:

1. **Candidate Intelligence:** Centralized management of canonical profiles and resume data.
2. **Role-Driven Discovery:** Automated job scraping, deduplication, and deep enrichment based on target role strategies.
3. **Scoring and Tailoring:** Transparent, fact-based job scoring paired with constraint-driven resume tailoring.
4. **Guarded Automation:** Step-based, browser-assisted execution of job applications utilizing Playwright.
5. **Diagnostics and Review:** Robust operator tooling, including OTP support, run logs, and explicit approval flows.

## Current Product Capabilities

The codebase currently supports the following capabilities:

- **Authentication:** Cookie-backed session management.
- **Profile Management:** Full CRUD operations for the canonical candidate profile, including automated resume upload and parsing.
- **Resume Export:** Access to an ATS-safe light theme catalog, packaged Markdown/LaTeX starter templates, and RenderCV-compatible input generation (with a reliable internal PDF fallback).
- **Job Discovery:** A robust role registry managing source subscriptions, supplemented by packaged discovery presets and a setup wizard.
- **Job Feed:** A near-realtime feed powered by ingestion runs and distinct feed events, featuring explicit transitions from discovery to enrichment to scoring.
- **Company Tracking:** A user-scoped directory managing company records, career portals, and recruiter contacts.
- **Tailoring Engine:** Transparent scoring logic and strict, fact-locked resume tailoring.
- **Application Execution:** Prepared application packets driving durable runs governed by a formal Finite State Machine (FSM), ensuring step logs are persisted even during partial failures.
- **Inbox Integrations:** Prepared OAuth paths for Gmail and Outlook, supporting in-run OTP retrieval.
- **Settings:** Exportable automation preference profiles.

## Core System Invariants

When modifying the system, you **must** preserve these fundamental invariants:

1. **The Canonical Profile is Absolute:** The candidate's master profile is the single source of truth.
2. **No Fabrication:** Generative outputs may optimize phrasing but must **never** invent or fabricate facts.
3. **Strategy-Driven Execution:** The user's Role Strategy dictates all discovery logic and automation policies.
4. **Separation of Concerns for Resumes:** Resume themes and starter templates act strictly as presentation layers; they do not store source data.
5. **Inspectable Automation:** Application runs must leave a durable, inspectable trail (logs, screenshots) even in the event of partial failures or unhandled pauses.
6. **Data Security:** Sensitive tokens, OTPs, and potentially risky application answers must always be masked or hidden behind explicit approval gates.

## Key Entry Points by Domain

### Resumes, Templates, and Document Export
- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`
- `apps/api/app/services/files.py`
- `apps/web/app/resume/page.tsx`

### Jobs, Roles, and Scoring Logic
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/company_directory.py`
- `apps/api/app/services/scoring.py`
- `apps/api/app/api/routes/roles.py`
- `apps/api/app/api/routes/jobs.py`
- `apps/api/app/api/routes/companies.py`

### Automation, Packets, and the FSM
- `apps/api/app/services/application_packets.py`
- `apps/api/app/services/application_fsm.py`
- `apps/api/app/services/user_preferences.py`
- `apps/api/app/api/routes/applications.py`
- `apps/api/app/api/routes/application_runs.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/persistence.py`
- `apps/worker/app/run_fsm.py`

### Settings, OTP, and Operator UX
- `apps/api/app/services/inbox.py`
- `apps/api/app/api/routes/inbox.py`
- `apps/web/components/forms/settings-form.tsx`
- `apps/web/app/applications/page.tsx`
- `apps/web/app/runs/[id]/page.tsx`

## AI Context Helpers

Before undertaking broad architectural changes, consult the project-local guidance files:
- **Product & Domain Knowledge:** `.agents/skills/applyforge-product/SKILL.md`
- **Operations Guidance:** `.agents/skills/applyforge-ops/SKILL.md`
- **Codex Agent Registry:** `.codex/config.toml`

## Required Verification Baseline

For any non-trivial changes to the codebase, you must pass the following checks:

1. **Python Compilation:**
   `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. **API Tests:**
   `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. **Worker Tests:**
   `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. **Web Frontend Checks (run inside `apps/web`):**
   - `npm run lint`
   - `npm run build`
   - `npm run typecheck` *(Note: `typecheck` is safest when run after `build` as `tsconfig.json` references `.next/types`.)*

## Current Reality Checks & Known Limitations

- **Worker Maturity:** While the background worker successfully handles enrichment and application execution, the Playwright field coverage remains at an MVP level.
- **Export Continuity:** Ensuring the resume export workflow remains functional is more critical than maintaining renderer purity. A RenderCV failure must gracefully degrade to the internal PDF fallback without breaking the user experience.
- **OAuth Status:** Although the OAuth code paths exist, connecting real provider credentials requires complete live verification in a deployed environment.
- **Documentation Standard:** Documentation must accurately describe the *current* state and behavior of the system, not future promises. Maintain this discipline in all PRs.
