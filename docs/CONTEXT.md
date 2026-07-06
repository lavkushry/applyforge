# ApplyForge Developer Context

This document serves as a foundational guide for developers working on ApplyForge, reducing the time needed to understand the project structure and product boundaries.

## Project Identity

ApplyForge functions as an operating system for the job search process, built around five core domains:
1. Unified candidate profile and intelligent resume management
2. Automated job discovery and deep enrichment driven by target roles
3. Objective scoring and precise document tailoring
4. Browser-based, operator-supervised application execution
5. System diagnostics, OTP handling, and manual review flows

## Current Product Capabilities

The existing implementation provides:
- Robust cookie-based authentication
- Full CRUD operations for the canonical candidate profile
- Resume parsing from uploaded documents
- Three ATS-optimized light themes for presentation
- Built-in Markdown and LaTeX starter templates
- Reliable PDF export with a RenderCV pipeline and internal fallback
- Configurable target roles and discovery source subscriptions
- A setup wizard with packaged presets for rapid onboarding
- Real-time job feeds powered by background ingestion and event tracking
- Structured records for companies, career portals, and recruiter contacts
- A clear progression from job discovery to enrichment and scoring
- Asynchronous, worker-based task processing
- Fact-based document tailoring that prevents hallucination
- Formal application packets ready for execution
- Immutable application runs with detailed step-level logging
- A strict finite state machine (FSM) for application run lifecycles
- Foundational OAuth support for Gmail and Outlook to support OTP flows
- User preference exports for future external automation

## Core System Invariants

When modifying the system, strictly uphold these rules:
1. **Single Source of Truth:** The canonical profile is the definitive record.
2. **No Hallucination:** Tailored output may rephrase, but it must never invent facts or skills.
3. **Role-Driven Actions:** Target roles dictate all discovery and automation behavior.
4. **Presentation Separation:** Themes and templates only format data; they do not store it.
5. **Durable Evidence:** Automation runs must retain their evidence (logs/screenshots) even if they crash.
6. **Security First:** Sensitive tokens, OTPs, and risky question responses must be masked or require explicit approval.

## File Navigation Guide

### Resumes, Templates, and Exports
- [resume_parser.py](../apps/api/app/services/resume_parser.py)
- [resume_themes.py](../apps/api/app/services/resume_themes.py)
- [resume_templates.py](../apps/api/app/services/resume_templates.py)
- [files.py](../apps/api/app/services/files.py)
- [resume/page.tsx](../apps/web/app/resume/page.tsx)

### Jobs, Roles, and Enrichment
- [role_ingestion.py](../apps/api/app/services/role_ingestion.py)
- [job_dispatch.py](../apps/api/app/services/job_dispatch.py)
- [job_enrichment.py](../apps/api/app/services/job_enrichment.py)
- [company_directory.py](../apps/api/app/services/company_directory.py)
- [scoring.py](../apps/api/app/services/scoring.py)
- [roles.py](../apps/api/app/api/routes/roles.py)
- [jobs.py](../apps/api/app/api/routes/jobs.py)
- [companies.py](../apps/api/app/api/routes/companies.py)

### Automation, FSM, and Execution
- [applications.py](../apps/api/app/api/routes/applications.py)
- [application_runs.py](../apps/api/app/api/routes/application_runs.py)
- [application_packets.py](../apps/api/app/services/application_packets.py)
- [application_fsm.py](../apps/api/app/services/application_fsm.py)
- [user_preferences.py](../apps/api/app/services/user_preferences.py)
- [playwright_runner.py](../apps/worker/app/playwright_runner.py)
- [persistence.py](../apps/worker/app/persistence.py)
- [run_fsm.py](../apps/worker/app/run_fsm.py)

### User Experience and Settings
- [settings-form.tsx](../apps/web/components/forms/settings-form.tsx)
- [inbox.py](../apps/api/app/services/inbox.py)
- [inbox.py](../apps/api/app/api/routes/inbox.py)
- [applications/page.tsx](../apps/web/app/applications/page.tsx)
- [runs/[id]/page.tsx](../apps/web/app/runs/[id]/page.tsx)

## Supplemental Guidelines

Consult these files for specialized context:
- Product and domain knowledge: [SKILL.md](../.agents/skills/applyforge-product/SKILL.md)
- Operational procedures: [SKILL.md](../.agents/skills/applyforge-ops/SKILL.md)
- Codex registry configuration: [config.toml](../.codex/config.toml)

## Mandatory Verification Suite

Before submitting substantial changes, run the following commands from the repository root:
1. `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. `npm run lint` in `apps/web`
5. `npm run build` in `apps/web`
6. `npm run typecheck` in `apps/web`
*(Ensure `typecheck` is run after `build` so `.next/types` are available).*

## Implementation Reality Checks
- The Playwright worker supports real execution, but field coverage is still expanding.
- Resume PDF export must succeed; if RenderCV fails, the internal fallback must take over.
- OAuth flows are structured, but live integration testing is required for new provider changes.
- Documentation must accurately reflect the *current* state of the code, not future plans.
