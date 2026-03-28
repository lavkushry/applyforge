# ApplyForge Architecture

## System Overview

ApplyForge is organized as a monorepo with three runtime applications:

1. `apps/web`
   - Next.js App Router frontend
   - TanStack Query for API state
   - React Hook Form + Zod for primary forms
   - Zustand for lightweight session and toast state

2. `apps/api`
   - FastAPI service
   - SQLAlchemy ORM models for normalized persistence
   - Pydantic schemas for request/response contracts
   - Deterministic AI task wrappers backed by prompt files and prompt metadata logging

3. `apps/worker`
   - Celery worker
   - Playwright runtime
   - Step-oriented assisted-apply skeleton with screenshots and pause-before-submit checkpoints

Supporting context artifacts live under:

- `docs` for product and architecture requirements,
- `.agents/skills` for ApplyForge-specific domain and operations guidance,
- `.codex/agents` for project-local Codex role definitions.

## Domain Boundaries

### 1. Authentication

- Cookie-backed JWT session token
- `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`
- MVP is single-tenant friendly but schema stays multi-user ready

### 2. Candidate Brain

- Resume upload and text extraction for PDF, DOCX, and TXT
- Parsed sections:
  - basics
  - summary
  - skills
  - experience
  - projects
  - education
  - certifications
  - links
- Fact-locked canonical profile acts as the source of truth for all downstream generation

### 3. Job Intake and Scoring

- Manual import by pasted description or URL metadata
- Company directory records sit between raw discovery and normalized jobs
- Jobs may resolve to a user-scoped `company_id` using normalized names and portal/hostname heuristics
- Discovery is separated from enrichment in the ingestion service:
  - discovery writes or refreshes the canonical job record,
  - enrichment writes structured sections, confidence metadata, and a raw snapshot artifact,
  - scoring is recorded against the resulting enrichment revision
- Normalization infers remote type, seniority, employment type, and tags
- Dedupe keys stop repeated inserts
- Target roles drive scrape cadence, score weighting inputs, and automation thresholds
- Job feed events preserve discovered, updated, enriched, score-changed, and expired lifecycle signals
- Scoring engine returns:
  - overall score
  - score breakdown
  - strengths
  - missing skills
  - reasons
  - recommendation
  - enrichment revision

### 4. Tailoring and Documents

- Tailored resume versions link a canonical resume to a job
- Resume themes are stored independently from canonical profile data
- RenderCV-compatible structured input can be produced from normalized resume content
- ATS-oriented PDF export writes to local storage abstraction with RenderCV-first fallback behavior
- Cover letters are generated per job and stored server-side
- Tailoring diffs now preserve:
  - matched and uncovered requirement signals
  - emphasized experience rows
  - emphasized project rows
  - source enrichment revision

### 4A. Company Intelligence

- `companies` provide canonical user-scoped company identity records
- `company_career_portals` preserve provider-specific careers metadata independently of jobs
- `company_contacts` preserve recruiter or HR context independently of jobs
- The thin company page is an internal operator surface for reviewing canonical company data, portals, contacts, and linked jobs

### 5. Inbox and OAuth Integrations

- Gmail and Outlook inbox connections are stored as user-scoped integrations
- OAuth start and callback routes issue signed state and PKCE for provider auth flows
- Access tokens are stored encrypted in metadata and sanitized out of API responses
- OTP retrieval can search provider inboxes directly or accept manually supplied messages

### 6. Automation Runs

- `applications` hold job-level progression states
- `application_runs` hold execution attempts
- `application_steps` hold checkpoint-level status, outputs, retries, and screenshots
- runs are created as queued records from the API and dispatched into the worker
- the worker writes durable step rows and screenshot file records directly into shared storage and the shared database
- preflight creates a prepared application packet before execution
- OTP lookup and approval gates are modeled as explicit step kinds
- Risky questions remain gated for explicit review

## Data Model Summary

Primary tables:

- `users`
- `candidate_profiles`
- `resumes`
- `resume_versions`
- `jobs`
- `companies`
- `company_career_portals`
- `company_contacts`
- `job_sources`
- `target_roles`
- `target_role_sources`
- `job_ingestion_runs`
- `job_feed_events`
- `job_scores`
- `cover_letters`
- `applications`
- `application_runs`
- `application_steps`
- `resume_themes`
- `inbox_connections`
- `inbox_otp_events`
- `uploaded_files`
- `settings`
- `audit_logs`

## Safety and Reliability Patterns

- Fact-locked tailoring with no invented claims
- Unknown application answers degrade to `Requires candidate review`
- Dedupe keys for job imports
- Prompt invocation logs stored in `audit_logs` with masked payload fragments
- Step-based application execution so paused and failed states are inspectable
- OAuth token material encrypted before storage and stripped from response payloads
- Provider readiness endpoints so setup failures can be diagnosed through the UI

## Context Landmarks For Future Work

If you need to continue product work quickly, start from these files:

- role discovery and job feed: [apps/api/app/services/role_ingestion.py](/home/ems/applyforge/apps/api/app/services/role_ingestion.py)
- enrichment stage and raw snapshot artifacts: [job_enrichment.py](/home/ems/applyforge/apps/api/app/services/job_enrichment.py)
- company matching and source resolution: [company_directory.py](/home/ems/applyforge/apps/api/app/services/company_directory.py), [companies.py](/home/ems/applyforge/apps/api/app/api/routes/companies.py)
- scoring and tailoring: [apps/api/app/services/scoring.py](/home/ems/applyforge/apps/api/app/services/scoring.py), [apps/api/app/services/tailor.py](/home/ems/applyforge/apps/api/app/services/tailor.py)
- resume themes and export: [apps/api/app/services/resume_themes.py](/home/ems/applyforge/apps/api/app/services/resume_themes.py), [apps/api/app/services/files.py](/home/ems/applyforge/apps/api/app/services/files.py)
- inbox OAuth and OTP flows: [apps/api/app/services/inbox.py](/home/ems/applyforge/apps/api/app/services/inbox.py), [apps/api/app/api/routes/inbox.py](/home/ems/applyforge/apps/api/app/api/routes/inbox.py)
- application packet and run dispatch: [application_packets.py](/home/ems/applyforge/apps/api/app/services/application_packets.py), [apps/api/app/api/routes/applications.py](/home/ems/applyforge/apps/api/app/api/routes/applications.py)
- run timeline behavior and durable worker persistence: [apps/worker/app/playwright_runner.py](/home/ems/applyforge/apps/worker/app/playwright_runner.py), [apps/worker/app/persistence.py](/home/ems/applyforge/apps/worker/app/persistence.py)
- settings UX and inbox connect UI: [apps/web/components/forms/settings-form.tsx](/home/ems/applyforge/apps/web/components/forms/settings-form.tsx)
- company directory UI: [page.tsx](/home/ems/applyforge/apps/web/app/companies/page.tsx)

## Migration Strategy

- The API currently bootstraps schema creation during local startup for MVP convenience
- Alembic scaffolding lives under `apps/api/alembic`
- Future hardening should remove `create_all` from runtime and rely on migrations only

## Frontend UX Strategy

- Clean SaaS shell with consistent cards, headers, and badges
- Empty states for unseeded views
- Toast feedback for mutations
- Detail pages kept thin by shared form and UI primitives

## AI Layer

Prompts live in `packages/prompts`:

- `resume_parse_cleanup.txt`
- `job_normalization.txt`
- `job_scoring_explainer.txt`
- `resume_tailoring.txt`
- `cover_letter.txt`
- `application_answering.txt`
- `risk_detection.txt`

The current implementation uses deterministic logic first and logs prompt metadata so swapping to a live OpenAI-compatible model later remains straightforward.
