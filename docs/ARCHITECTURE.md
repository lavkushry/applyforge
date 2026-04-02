# ApplyForge Architecture

## System Overview

ApplyForge utilizes a modern monorepo structure, distributing functionality across three primary runtime applications and a modular configuration layer:

1. **`apps/web`**: The user-facing frontend.
   - Built with Next.js (App Router).
   - Utilizes TanStack Query for robust API state management.
   - Implements React Hook Form and Zod for reliable form handling and validation.
   - Employs Zustand for efficient session and toast state management.

2. **`apps/api`**: The core backend service.
   - Developed using FastAPI.
   - Relies on SQLAlchemy ORM for database modeling and persistence.
   - Uses Pydantic schemas to strictly define request and response contracts.
   - Houses deterministic-first services responsible for job scoring, resume tailoring, document parsing, PDF export, and workflow orchestration.

3. **`apps/worker`**: The background execution engine.
   - Powered by Celery for task queueing.
   - Utilizes Playwright for robust browser automation.
   - Manages job enrichment execution.
   - Drives the step-based application runner, ensuring durable screenshot capture and handling strategic pause gates.

4. **`packages/config`**: The centralized configuration registry.
   - Contains discovery presets for job sourcing.
   - Houses standard resume template assets.
   - Serves as the future repository for additional packaged product defaults.

**Supporting Artifacts:**
- `docs/`: Comprehensive product, architecture, and roadmap documentation.
- `.agents/skills/`: Domain and operations guidance tailored specifically for ApplyForge.
- `.codex/agents/`: Project-local Codex role definitions.

## Core Architectural Subsystems

ApplyForge operates through five deeply integrated subsystems. Crucially, all subsystems adhere to a single product invariant: **The canonical candidate profile is the absolute, trusted source of truth for all resume facts.**

### 1. Authentication and User Scope
- Implements a secure, cookie-backed JWT session flow.
- Enforces request-scoped IDs and generates structured logs for all API responses to ensure traceability.
- Applies strict rate limiting on authentication and inbox-sensitive endpoints.
- Maintains strict user-scoping for profiles, jobs, target roles, company intelligence, inbox connections, and applications.
- **Key Routes:** `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`.

### 2. Candidate Intelligence ("The Brain")
- Handles resume uploads and precise text extraction across PDF, DOCX, and TXT formats.
- Parses unstructured text into structured profile sections: basics, summary, skills, experience, projects, education, certifications, and links.
- Ensures the `candidate_profiles` table remains completely fact-locked.
- Provides a comprehensive web profile editor for manual adjustments to parsed sections and critical apply-preferences (e.g., saved answers).
- Persists user-specific settings, including automation preferences, job filters, and default resume styling.
- Exposes a portable user-preference export mechanism, facilitating future automation tooling and operator reviews.

### 3. Resume Theming, Templates, and Export
- Ships with three built-in, ATS-safe light themes.
- Employs a RenderCV-compatible builder for structured input processing.
- Includes a reliable internal fallback renderer to ensure PDF generation never fails if RenderCV encounters an error.
- Leverages packaged assets (`sections.json`, `resume_template.md`, `resume_template.tex`) located in `packages/config/resume/`.
- Provides a developer CLI for listing, rendering, and exporting templates.
- The web UI allows users to select themes, browse templates, and preview rendered Markdown or LaTeX source code prior to export.

### 4. Role-Driven Discovery and Enrichment
- Utilizes `target_roles` to define user strategy, storing parameters such as aliases, keywords, location preferences, salary targets, visa requirements, seniority, company inclusion/exclusion lists, and automation thresholds.
- Manages source subscriptions via `target_role_sources`.
- The `packages/config/discovery/` registry provides essential source presets, search templates, and global domain blocklists.
- The ingestion pipeline is explicitly split into three phases: discovery (finding the job), worker-queued enrichment (fetching deep details), and revision-aware scoring.
- Job lifecycles are durably tracked via explicit feed events: `discovered`, `enriched`, `score_changed`, and `expired`.

### 5. Company Intelligence
- The `companies` table provides canonical, user-scoped company identities.
- `company_career_portals` stores provider-specific metadata for direct integration.
- `company_contacts` maintains recruiter and HR context independent of specific job records.
- The system attempts to resolve raw job text to known company entities using deterministic heuristics.

### 6. Scoring and Tailoring Engines
- The scoring algorithm evaluates jobs based on the intersection of the canonical profile, the active target role, and the current enrichment revision.
- Scoring outputs provide high transparency, detailing the overall score, granular breakdown, identified strengths, missing skills, clear reasoning, and a final recommendation.
- The tailoring engine strictly preserves the user's factual data while emphasizing highly relevant experience and projects to address specific job requirements.
- Job-specific cover letters are automatically generated and stored alongside the job record.

### 7. Application Packets and Run Orchestration
- `applications` track the overarching job-level application intent.
- `application_runs` record specific execution attempts.
- `application_steps` store granular, step-level evidence (logs, screenshots).
- The preflight sequence constructs a formal application packet containing resolved answers, data provenance, linked documents, identified blocking issues, risk summaries, and an auto-submit eligibility flag.
- Runs are strictly governed by a formal Finite State Machine (FSM) utilizing explicit transitions: `queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`.

### 8. Worker Execution and Persistence
- Celery workers write outputs directly to the shared PostgreSQL database and file storage systems.
- The `RunRecorder` service reliably persists step data and FSM status changes.
- Playwright-captured screenshots are durably stored as `uploaded_files`.
- The `application_runs` table retains comprehensive retry and backoff histories.
- The Playwright runner is equipped with capabilities including: intelligent navigation, text field entry, complex adapter handling (selects, radios, dates), resume uploading, multi-step transition management, anti-bot detection, unsupported-field pausing, assisted pause-before-submit workflows, and submit-confirmation detection.

### 9. Inbox Integration and OTP Support
- Provides robust OAuth integrations for Gmail and Outlook.
- Reports provider readiness status directly within the user settings UI.
- Ensures highly secure, encrypted storage of tokens and strictly sanitizes API responses to prevent leakage.
- The OTP retrieval pipeline supports automated provider inbox fetching, manual entry fallbacks, and masked event logging.
- Crucially, OTP retrieval processes are modeled as first-class, inspectable steps within the run timeline.

## Data Persistence Model

The core relational schema is built on PostgreSQL. Key tables include:

**User & Profile Domain:**
- `users`, `candidate_profiles`, `settings`, `inbox_connections`

**Document Domain:**
- `resumes`, `resume_versions`, `resume_themes`, `cover_letters`, `uploaded_files`

**Discovery Domain:**
- `target_roles`, `target_role_sources`, `jobs`, `job_scores`, `job_sources`, `job_ingestion_runs`, `job_feed_events`

**Company Domain:**
- `companies`, `company_career_portals`, `company_contacts`

**Execution Domain:**
- `applications`, `application_runs`, `application_steps`, `inbox_otp_events`, `audit_logs`

## Primary System Workflows

### The Resume Pipeline
1. Ingest source resume (PDF, DOCX, TXT).
2. Extract raw text.
3. Parse text into the structured canonical profile.
4. User selects a theme or starter template.
5. Generate a targeted, tailored variant.
6. Export the final PDF utilizing the primary RenderCV pipeline or the internal fallback.

### The Discovery Pipeline
1. User defines a target role strategy.
2. System attaches relevant packaged or manual source presets.
3. Execute scheduled or manual discovery runs.
4. Normalize and insert newly discovered jobs (handling deduplication).
5. Dispatch queued enrichment tasks for new jobs.
6. Calculate scores and emit relevant feed events upon enrichment completion.

### The Application Pipeline
1. System prepares a comprehensive application packet.
2. Generate a `queued` application run.
3. Dispatch the task to the Celery worker.
4. Worker executes, persisting steps, capturing screenshots, and handling pauses.
5. Retrieve required OTPs via inbox integration (if applicable).
6. Transition the run through the FSM to terminal or paused states (`completed`, `failed`, `paused`, `uncertain`).

## Safety and Reliability Mechanisms

- **Strict Factual Adherence:** The tailoring engine is locked; it cannot invent claims or fabricate experience.
- **Approval Gates:** Explicit manual approval is required for questions flagged as risky (e.g., legal or compensation inquiries).
- **Graceful Degradation:** Unknown answers default to requiring manual candidate review rather than guessing.
- **Bot Compliance:** Encounters with CAPTCHAs or advanced anti-bot challenges result in an immediate pause, handing control back to the user instead of attempting circumvention.
- **Data Integrity:** Robust deduplication keys prevent redundant job insertions during discovery.
- **Traceability:** Request IDs and highly structured logs ensure complete traceability across both API and worker environments. Application run histories explicitly expose screenshot evidence and retry metadata to the operator.
- **Security:** Provider tokens and OTP codes are strictly masked in logs and encrypted at rest.
- **Durability:** Worker execution evidence (screenshots, step logs) remains durable and inspectable even in the event of a partial workflow failure.

## Codebase Entry Points

For rapid orientation, start with these key files:

**Resume & Document Generation:**
- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`
- `apps/api/app/services/files.py`
- `apps/api/app/api/routes/resume_templates.py`

**Discovery, Enrichment & Scoring:**
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/company_directory.py`
- `apps/api/app/services/scoring.py`

**Automation & Preferences:**
- `apps/api/app/services/application_packets.py`
- `apps/api/app/services/application_fsm.py`
- `apps/api/app/services/user_preferences.py`
- `apps/api/app/api/routes/applications.py`
- `apps/api/app/api/routes/application_runs.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/persistence.py`
- `apps/worker/app/run_fsm.py`

**Key Frontend Surfaces:**
- `apps/web/app/resume/page.tsx`
- `apps/web/app/jobs/page.tsx`
- `apps/web/app/applications/page.tsx`
- `apps/web/components/forms/settings-form.tsx`
- `apps/web/app/companies/page.tsx`
- `apps/web/app/wizard/page.tsx`

## Technical Notes

- **Database Migrations:** The API currently utilizes `create_all` during startup for MVP convenience. This should be transitioned to a strictly Alembic-managed migration flow in future iterations.

## Development Verification Baseline

When submitting non-trivial changes, ensure the following baseline checks pass:

1. **Compile Check:**
   `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. **API Tests:**
   `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. **Worker Tests:**
   `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. **Web Checks:**
   Navigate to `apps/web` and run:
   - `npm run lint`
   - `npm run build`
   - `npm run typecheck` *(Note: `typecheck` is safest when run after `build` as `tsconfig.json` references `.next/types`.)*
