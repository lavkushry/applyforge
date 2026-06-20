<!-- REWRITTEN DOCUMENT: CONTEXT.md -->
<!-- This document has been comprehensively reviewed and rewritten for clarity and consistency. -->

# ApplyForge Context Guide

This document is provided to reduce rediscovery cost in future sessions.

## Section: What ApplyForge Is

ApplyForge is a job-hunt operating system with five connected loops:

1. canonical profile and resume intelligence
2. role-driven discovery and enrichment
3. transparent scoring and tailoring
4. guarded browser-assisted application execution
5. diagnostics, OTP support, and operator review

## Section: Current Product Shape

The repository already supports:

- cookie-backed auth
- canonical profile Create, Read, Update, Delete
- resume upload and parsing
- ATS-safe light theme catalog
- packaged Markdown and LaTeX resume starter templates
- RenderCV-compatible input generation with internal PDF fallback
- role registry and source subscriptions
- packaged discovery presets and setup wizard bootstrapping
- near-realtime feed backed by ingestion runs and feed events
- company directory records, portals, and recruiter contacts
- explicit discovery -> enrichment -> scoring transitions
- worker-queued enrichment
- transparent scoring and fact-locked tailoring
- prepared application packets
- durable application runs and step logs
- formal run FSM transitions
- Gmail and Outlook OAuth readiness plus OTP retrieval
- exported automation preference profile in Settings

## Section: Invariants You Should Preserve

1. Canonical profile data is authoritative.
2. Generated output may optimize phrasing, but may not fabricate facts.
3. Role strategy is the controlling input for discovery and automation policy.
4. Resume themes and starter templates are presentation layers, not sources of truth.
5. Application automation must remain inspectable after partial failure.
6. Sensitive tokens, OTPs, and risky answers must stay masked or approval-gated.

## Section: Best Entry Points By Task

### Resume, templates, and export

- [resume_parser.py](../apps/api/app/services/resume_parser.py)
- [resume_themes.py](../apps/api/app/services/resume_themes.py)
- [resume_templates.py](../apps/api/app/services/resume_templates.py)
- [files.py](../apps/api/app/services/files.py)
- [resume/page.tsx](../apps/web/app/resume/page.tsx)

### Jobs, roles, and scoring

- [role_ingestion.py](../apps/api/app/services/role_ingestion.py)
- [job_dispatch.py](../apps/api/app/services/job_dispatch.py)
- [job_enrichment.py](../apps/api/app/services/job_enrichment.py)
- [company_directory.py](../apps/api/app/services/company_directory.py)
- [scoring.py](../apps/api/app/services/scoring.py)
- [roles.py](../apps/api/app/api/routes/roles.py)
- [jobs.py](../apps/api/app/api/routes/jobs.py)
- [companies.py](../apps/api/app/api/routes/companies.py)

### Automation, packets, and FSM

- [applications.py](../apps/api/app/api/routes/applications.py)
- [application_runs.py](../apps/api/app/api/routes/application_runs.py)
- [application_packets.py](../apps/api/app/services/application_packets.py)
- [application_fsm.py](../apps/api/app/services/application_fsm.py)
- [user_preferences.py](../apps/api/app/services/user_preferences.py)
- [playwright_runner.py](../apps/worker/app/playwright_runner.py)
- [persistence.py](../apps/worker/app/persistence.py)
- [run_fsm.py](../apps/worker/app/run_fsm.py)

### Settings, OTP, and operator UX

- [settings-form.tsx](../apps/web/components/forms/settings-form.tsx)
- [inbox.py](../apps/api/app/services/inbox.py)
- [inbox.py](../apps/api/app/api/routes/inbox.py)
- [applications/page.tsx](../apps/web/app/applications/page.tsx)
- [runs/[id]/page.tsx](../apps/web/app/runs/[id]/page.tsx)

## Section: Project-Local Context Helpers

Use the project-local skill and agent files before broad exploration:

- product/domain guidance: [SKILL.md](../.agents/skills/applyforge-product/SKILL.md)
- operations guidance: [SKILL.md](../.agents/skills/applyforge-ops/SKILL.md)
- Codex agent registry: [config.toml](../.codex/config.toml)

## Section: Current Verification Baseline

When making nontrivial changes, the expected baseline checks are:

1. `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. `npm run lint` in `apps/web`
5. `npm run build` in `apps/web`
6. `npm run typecheck` in `apps/web`

Note: in this repo, `typecheck` is safest after `build` because `tsconfig.json` includes `.next/types`.

## Section: Current Reality Checks

- The worker path is real for enrichment and application execution, but still Minimum Viable Product-level in field coverage.
- Resume export continuity matters more than renderer purity; RenderCV failure must not break export.
- OAuth code paths are implemented, but real provider credentials still need full live verification.
- Docs should describe current behavior, not future promise. Preserve that discipline.
