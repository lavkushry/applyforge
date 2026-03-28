# ApplyForge Architecture

## System Overview

ApplyForge is a monorepo with three runtime applications and a small packaged config layer:

1. `apps/web`
   - Next.js App Router frontend
   - TanStack Query for API state
   - React Hook Form + Zod for forms
   - Zustand for session and toast state

2. `apps/api`
   - FastAPI service
   - SQLAlchemy ORM models for persistence
   - Pydantic schemas for request and response contracts
   - deterministic-first services for scoring, tailoring, parsing, export, and orchestration

3. `apps/worker`
   - Celery worker
   - Playwright runtime
   - job enrichment executor
   - step-based application runner with durable screenshots and pause gates

4. `packages/config`
   - discovery preset registry
   - resume template assets
   - future home for more packaged product defaults

Supporting context artifacts live under:

- `docs` for product, architecture, and roadmap documentation
- `.agents/skills` for ApplyForge-specific domain and ops guidance
- `.codex/agents` for project-local Codex role definitions

## Current Architectural Shape

ApplyForge now behaves like five connected subsystems:

1. canonical profile and resume intelligence
2. role-driven discovery, enrichment, and scoring
3. company intelligence and source resolution
4. tailored document generation and export
5. guarded application automation with diagnostics and OTP support

Those subsystems share one product invariant: the canonical candidate profile is the only trusted source of resume facts.

## Domain Boundaries

### 1. Auth and user scope

- Cookie-backed JWT session flow
- user-scoped profile, jobs, roles, companies, inbox connections, and applications
- routes:
  - `/auth/register`
  - `/auth/login`
  - `/auth/logout`
  - `/auth/me`

### 2. Candidate brain

- resume upload and text extraction for PDF, DOCX, and TXT
- parsed sections:
  - basics
  - summary
  - skills
  - experience
  - projects
  - education
  - certifications
  - links
- `candidate_profiles` remains fact-locked and authoritative
- profile settings persist:
  - automation preferences
  - job filters
  - resume preferences
- a portable user-preference export now exists for operators and future automation tooling

### 3. Resume themes, templates, and export

- three built-in ATS-safe light themes
- RenderCV-compatible structured input builder
- internal PDF fallback renderer when RenderCV fails
- packaged resume-template assets:
  - `packages/config/resume/sections.json`
  - `packages/config/resume/resume_template.md`
  - `packages/config/resume/resume_template.tex`
- a small CLI exists for template listing, template rendering, and PDF export
- web resume page exposes:
  - theme selection
  - template browsing
  - rendered Markdown or LaTeX source preview

### 4. Role-driven discovery and enrichment

- `target_roles` define:
  - aliases
  - keywords
  - preferred locations
  - remote preference
  - salary target
  - visa preference
  - seniority
  - company include/exclude lists
  - automation threshold
- `target_role_sources` define source subscriptions
- packaged discovery registry provides:
  - source presets
  - search templates
  - blocked domains
- ingestion is split into:
  - discovery
  - worker-queued enrichment
  - revision-aware scoring
- job lifecycle is preserved through feed events:
  - discovered
  - enriched
  - score_changed
  - expired

### 5. Company intelligence

- `companies` provide canonical user-scoped company identity
- `company_career_portals` preserve provider-specific careers metadata
- `company_contacts` preserve recruiter and HR context independently of job records
- jobs can resolve through company heuristics before staying as raw text only

### 6. Scoring and tailoring

- scoring now depends on:
  - canonical profile
  - target role
  - enrichment revision
- score output includes:
  - overall score
  - breakdown
  - strengths
  - missing skills
  - reasons
  - recommendation
- tailoring preserves:
  - matched requirements
  - uncovered requirements
  - emphasized experience
  - emphasized projects
  - source enrichment revision
- cover letters are generated and stored per job

### 7. Application packets and run orchestration

- `applications` represent the job-level application record
- `application_runs` represent execution attempts
- `application_steps` represent step-level evidence
- preflight builds a formal application packet before execution
- packet contains:
  - resolved answers
  - provenance
  - resume file linkage
  - cover-letter linkage
  - blocking issues
  - risk summary
  - auto-submit eligibility
- a formal FSM now governs run transitions:
  - `queued`
  - `running`
  - `paused`
  - `failed`
  - `completed`
  - `uncertain`

### 8. Worker execution and persistence

- worker writes directly into shared database and file storage
- `RunRecorder` persists step rows and status changes
- screenshots are persisted as `uploaded_files`
- application runner currently supports:
  - navigation
  - common text fields
  - resume upload
  - anti-bot detection
  - unsupported required-field pause
  - assisted pause-before-submit
  - submit confirmation detection

### 9. Inbox and OTP

- Gmail and Outlook OAuth integrations
- provider readiness reporting in the UI
- encrypted token storage and sanitized API responses
- OTP retrieval supports:
  - provider inbox fetch
  - manual message payload fallback
  - masked event logging
- OTP steps are first-class run steps

## Key Persistence Model

Primary tables:

- `users`
- `candidate_profiles`
- `resumes`
- `resume_versions`
- `resume_themes`
- `jobs`
- `job_scores`
- `job_sources`
- `target_roles`
- `target_role_sources`
- `job_ingestion_runs`
- `job_feed_events`
- `companies`
- `company_career_portals`
- `company_contacts`
- `cover_letters`
- `applications`
- `application_runs`
- `application_steps`
- `inbox_connections`
- `inbox_otp_events`
- `uploaded_files`
- `settings`
- `audit_logs`

## Main Runtime Flows

### Resume flow

1. upload source resume
2. extract raw text
3. parse into canonical profile
4. select theme or starter template
5. generate tailored version
6. export PDF through RenderCV-first fallback pipeline

### Discovery flow

1. create target role
2. attach packaged or manual sources
3. run discovery
4. insert or refresh normalized jobs
5. dispatch enrichment per job
6. write score and feed events

### Apply flow

1. prepare application packet
2. create queued run
3. dispatch worker
4. persist steps, screenshots, and pauses
5. request OTP if needed
6. pause, fail, complete, or mark uncertain through the FSM

## Safety and Reliability Patterns

- fact-locked tailoring with no invented claims
- explicit risky-question approval gates
- unknown answers degrade to candidate review
- CAPTCHA and anti-bot flows pause rather than bypass
- dedupe keys protect discovery from duplicate inserts
- provider tokens and OTPs stay masked or encrypted
- worker evidence remains durable after partial failure

## Best File Entry Points

### Resume and document flows

- [resume_parser.py](/home/ems/applyforge/apps/api/app/services/resume_parser.py)
- [resume_themes.py](/home/ems/applyforge/apps/api/app/services/resume_themes.py)
- [resume_templates.py](/home/ems/applyforge/apps/api/app/services/resume_templates.py)
- [files.py](/home/ems/applyforge/apps/api/app/services/files.py)
- [resume_templates.py](/home/ems/applyforge/apps/api/app/api/routes/resume_templates.py)

### Discovery and scoring

- [role_ingestion.py](/home/ems/applyforge/apps/api/app/services/role_ingestion.py)
- [job_dispatch.py](/home/ems/applyforge/apps/api/app/services/job_dispatch.py)
- [job_enrichment.py](/home/ems/applyforge/apps/api/app/services/job_enrichment.py)
- [company_directory.py](/home/ems/applyforge/apps/api/app/services/company_directory.py)
- [scoring.py](/home/ems/applyforge/apps/api/app/services/scoring.py)

### Automation and preferences

- [application_packets.py](/home/ems/applyforge/apps/api/app/services/application_packets.py)
- [application_fsm.py](/home/ems/applyforge/apps/api/app/services/application_fsm.py)
- [user_preferences.py](/home/ems/applyforge/apps/api/app/services/user_preferences.py)
- [applications.py](/home/ems/applyforge/apps/api/app/api/routes/applications.py)
- [application_runs.py](/home/ems/applyforge/apps/api/app/api/routes/application_runs.py)
- [playwright_runner.py](/home/ems/applyforge/apps/worker/app/playwright_runner.py)
- [persistence.py](/home/ems/applyforge/apps/worker/app/persistence.py)
- [run_fsm.py](/home/ems/applyforge/apps/worker/app/run_fsm.py)

### UX surfaces

- [resume/page.tsx](/home/ems/applyforge/apps/web/app/resume/page.tsx)
- [jobs/page.tsx](/home/ems/applyforge/apps/web/app/jobs/page.tsx)
- [applications/page.tsx](/home/ems/applyforge/apps/web/app/applications/page.tsx)
- [settings-form.tsx](/home/ems/applyforge/apps/web/components/forms/settings-form.tsx)
- [companies/page.tsx](/home/ems/applyforge/apps/web/app/companies/page.tsx)
- [wizard/page.tsx](/home/ems/applyforge/apps/web/app/wizard/page.tsx)

## Migration Note

- The API still calls `create_all` at startup for local MVP convenience.
- Long term, runtime schema creation should be removed in favor of Alembic-only migrations.

## Verification Baseline

For nontrivial changes, the expected baseline is:

1. `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. `npm run lint` in `apps/web`
5. `npm run build` in `apps/web`
6. `npm run typecheck` in `apps/web`

Note: in this repo, `typecheck` is safest after `build` because `tsconfig.json` includes `.next/types`.
