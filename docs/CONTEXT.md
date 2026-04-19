# ApplyForge Context Guide

This document is designed to rapidly orient developers in future sessions by minimizing rediscovery costs.

## What ApplyForge Is

ApplyForge operates as a comprehensive job-hunt operating system driven by five interconnected loops:

1. Canonical profile and resume intelligence.
2. Role-driven discovery and data enrichment.
3. Transparent scoring and fact-locked tailoring.
4. Guarded, browser-assisted application execution.
5. Extensive diagnostics, OTP support, and operator review tooling.

## Current Product Shape

The repository is mature and actively supports the following core features:

- Cookie-backed authentication.
- Canonical profile CRUD operations.
- Resume upload accompanied by reliable parsing.
- An ATS-safe light theme catalog.
- Packaged Markdown and LaTeX resume starter templates.
- RenderCV-compatible input generation featuring an internal PDF fallback.
- Comprehensive role registries and source subscriptions.
- Packaged discovery presets alongside setup wizard bootstrapping.
- A near-realtime feed backed by ingestion runs and robust feed events.
- Company directory records, career portals, and recruiter contacts.
- Explicit transitions across discovery, enrichment, and scoring phases.
- Worker-queued job enrichment.
- Transparent scoring and rigorous fact-locked tailoring.
- Dynamically prepared application packets.
- Durable application runs maintaining reliable step logs.
- Formal run FSM (Finite State Machine) transitions.
- Gmail and Outlook OAuth readiness coupled with OTP retrieval capabilities.
- An exported automation preference profile readily accessible in Settings.

## Core Invariants to Preserve

1. **The Canonical Profile is Absolute:** The candidate profile data remains the authoritative source of truth.
2. **No Hallucinations:** Generated outputs may optimize phrasing, but they must *never* fabricate or invent facts.
3. **Role Strategy Controls:** The user's role strategy dictates both discovery focus and automation policies.
4. **Templates are Presentation Only:** Resume themes and starter templates solely handle presentation; they are not data sources.
5. **Durable Evidence:** Application automation must always remain inspectable, especially following partial failures.
6. **Protect Sensitive Data:** Sensitive tokens, OTPs, and risky application answers must consistently remain masked or require explicit manual approval.

## Best Entry Points By Task

### Resumes, Templates & Export
- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`
- `apps/api/app/services/files.py`
- `apps/web/app/resume/page.tsx`

### Jobs, Roles & Scoring
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/company_directory.py`
- `apps/api/app/services/scoring.py`
- `apps/api/app/api/routes/roles.py`
- `apps/api/app/api/routes/jobs.py`
- `apps/api/app/api/routes/companies.py`

### Automation, Packets & FSM
- `apps/api/app/api/routes/applications.py`
- `apps/api/app/api/routes/application_runs.py`
- `apps/api/app/services/application_packets.py`
- `apps/api/app/services/application_fsm.py`
- `apps/api/app/services/user_preferences.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/persistence.py`
- `apps/worker/app/run_fsm.py`

### Settings, OTP & Operator UX
- `apps/web/components/forms/settings-form.tsx`
- `apps/api/app/services/inbox.py`
- `apps/api/app/api/routes/inbox.py`
- `apps/web/app/applications/page.tsx`
- `apps/web/app/runs/[id]/page.tsx`

## Project-Local Context Helpers

Leverage the included project-local skill and agent files prior to undertaking broad exploration:

- **Product/Domain Guidance:** `.agents/skills/applyforge-product/SKILL.md`
- **Operations Guidance:** `.agents/skills/applyforge-ops/SKILL.md`
- **Codex Agent Registry:** `.codex/config.toml`

## Current Verification Baseline

When implementing nontrivial changes, ensure the codebase satisfies these baseline checks:

1. `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. `npm run lint` in `apps/web`
5. `npm run build` in `apps/web`
6. `npm run typecheck` in `apps/web`

*Note: Within this repository, running `typecheck` is safest after executing `build` since `tsconfig.json` includes `.next/types`.*

## Current Reality Checks

- The worker pathway reliably handles enrichment and application execution, though field coverage remains at MVP scale.
- Continuous resume export availability takes precedence over strict renderer purity; a RenderCV failure gracefully triggers an internal fallback so exports remain uninterrupted.
- OAuth logic is thoroughly implemented, though real provider credentials require live end-to-end verification.
- Maintain discipline: Documentation must strictly describe the system's *current* behavior, not future promises.
