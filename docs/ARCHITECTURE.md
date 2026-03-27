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
- Normalization infers remote type, seniority, employment type, and tags
- Dedupe keys stop repeated inserts
- Scoring engine returns:
  - overall score
  - score breakdown
  - strengths
  - missing skills
  - reasons
  - recommendation

### 4. Tailoring and Documents

- Tailored resume versions link a canonical resume to a job
- ATS-oriented PDF export writes to local storage abstraction
- Cover letters are generated per job and stored server-side

### 5. Automation Runs

- `applications` hold job-level progression states
- `application_runs` hold execution attempts
- `application_steps` hold checkpoint-level status, outputs, retries, and screenshots
- Risky questions remain gated for explicit review

## Data Model Summary

Primary tables:

- `users`
- `candidate_profiles`
- `resumes`
- `resume_versions`
- `jobs`
- `job_sources`
- `job_scores`
- `cover_letters`
- `applications`
- `application_runs`
- `application_steps`
- `uploaded_files`
- `settings`
- `audit_logs`

## Safety and Reliability Patterns

- Fact-locked tailoring with no invented claims
- Unknown application answers degrade to `Requires candidate review`
- Dedupe keys for job imports
- Prompt invocation logs stored in `audit_logs` with masked payload fragments
- Step-based application execution so paused and failed states are inspectable

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
