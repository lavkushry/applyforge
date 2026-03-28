# ApplyForge Context Guide

This file exists to reduce rediscovery cost in future sessions.

## What ApplyForge Is

ApplyForge is a job-hunt operating system with four connected loops:

1. canonical profile and resume intelligence,
2. role-driven job discovery and scoring,
3. tailored document generation,
4. guarded application automation with diagnostics.

## Current Product Shape

The repository already supports:

- cookie-backed auth,
- canonical profile CRUD,
- resume upload and parsing,
- role registry and scrape preferences,
- company directory records, portals, and recruiter contacts,
- near-realtime role feed from ingestion runs,
- transparent scoring and fact-locked tailoring,
- theme-aware resume versions,
- PDF export with RenderCV-compatible input and internal fallback,
- inbox OAuth readiness plus Gmail/Outlook OTP retrieval,
- application runs with durable step logs and pause gates.

## Invariants You Should Preserve

1. Canonical profile data is authoritative.
2. Generated output may optimize phrasing, but may not fabricate facts.
3. Role strategy is the controlling input for discovery and automation policy.
4. Application automation must remain inspectable after partial failure.
5. Sensitive tokens, OTPs, and risky answers must stay masked or approval-gated.

## Best Entry Points By Task

### Resume and tailoring

- [apps/api/app/services/resume_parser.py](/home/ems/applyforge/apps/api/app/services/resume_parser.py)
- [apps/api/app/services/tailor.py](/home/ems/applyforge/apps/api/app/services/tailor.py)
- [apps/api/app/services/resume_themes.py](/home/ems/applyforge/apps/api/app/services/resume_themes.py)
- [apps/api/app/services/files.py](/home/ems/applyforge/apps/api/app/services/files.py)

### Jobs and scoring

- [apps/api/app/services/job_normalizer.py](/home/ems/applyforge/apps/api/app/services/job_normalizer.py)
- [apps/api/app/services/company_directory.py](/home/ems/applyforge/apps/api/app/services/company_directory.py)
- [apps/api/app/services/scoring.py](/home/ems/applyforge/apps/api/app/services/scoring.py)
- [apps/api/app/services/role_ingestion.py](/home/ems/applyforge/apps/api/app/services/role_ingestion.py)
- [apps/api/app/api/routes/jobs.py](/home/ems/applyforge/apps/api/app/api/routes/jobs.py)
- [apps/api/app/api/routes/companies.py](/home/ems/applyforge/apps/api/app/api/routes/companies.py)
- [apps/api/app/api/routes/roles.py](/home/ems/applyforge/apps/api/app/api/routes/roles.py)

### Automation and OTP

- [apps/api/app/api/routes/applications.py](/home/ems/applyforge/apps/api/app/api/routes/applications.py)
- [apps/api/app/automation/engine.py](/home/ems/applyforge/apps/api/app/automation/engine.py)
- [apps/api/app/services/inbox.py](/home/ems/applyforge/apps/api/app/services/inbox.py)
- [apps/api/app/api/routes/inbox.py](/home/ems/applyforge/apps/api/app/api/routes/inbox.py)

### Web surface

- [apps/web/app/dashboard/page.tsx](/home/ems/applyforge/apps/web/app/dashboard/page.tsx)
- [apps/web/app/jobs/page.tsx](/home/ems/applyforge/apps/web/app/jobs/page.tsx)
- [apps/web/app/companies/page.tsx](/home/ems/applyforge/apps/web/app/companies/page.tsx)
- [apps/web/app/resume/page.tsx](/home/ems/applyforge/apps/web/app/resume/page.tsx)
- [apps/web/components/forms/settings-form.tsx](/home/ems/applyforge/apps/web/components/forms/settings-form.tsx)
- [apps/web/lib/types.ts](/home/ems/applyforge/apps/web/lib/types.ts)

## Context For Future Agents

Use the project-local skill and agent files before broad exploration:

- product/domain guidance: [SKILL.md](/home/ems/applyforge/.agents/skills/applyforge-product/SKILL.md)
- operations guidance: [SKILL.md](/home/ems/applyforge/.agents/skills/applyforge-ops/SKILL.md)
- Codex agent registry: [config.toml](/home/ems/applyforge/.codex/config.toml)

## Verification Baseline

When making nontrivial changes, the expected baseline checks are:

1. `python3 -m compileall apps/api/app apps/api/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `npm run lint` in `apps/web`
4. `npm run build` in `apps/web`
5. `npm run typecheck` in `apps/web`

Note: in this repo, `typecheck` is safest after `build` because `tsconfig.json` includes `.next/types`.
