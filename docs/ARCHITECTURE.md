# ApplyForge Architecture

## System Overview

ApplyForge operates as a monorepo containing three distinct runtime applications alongside a shared configuration package layer:

1.  **`apps/web`**
    *   Next.js App Router frontend framework.
    *   TanStack Query for robust API state management.
    *   React Hook Form combined with Zod for robust form validation.
    *   Zustand for managing global session and toast notification state.

2.  **`apps/api`**
    *   FastAPI backend service.
    *   SQLAlchemy ORM models managing data persistence.
    *   Pydantic schemas enforcing request and response contracts.
    *   Deterministic-first services handling scoring, document tailoring, data parsing, exports, and system orchestration.

3.  **`apps/worker`**
    *   Celery task worker.
    *   Playwright runtime for browser automation.
    *   Job enrichment execution engine.
    *   Step-based application runner featuring durable screenshot capture and logic-driven pause gates.

4.  **`packages/config`**
    *   Discovery preset registry defining job board targets.
    *   Resume template assets defining structural layouts.
    *   Designated home for future packaged product defaults.

Supporting context artifacts are located in:
*   `docs`: Product requirements, architectural specifications, and roadmap details.
*   `.agents/skills`: Domain-specific and operational guidance for ApplyForge.
*   `.codex/agents`: Definitions for project-local Codex roles.

## Current Architectural Subsystems

ApplyForge is structured around five tightly connected subsystems:

1.  Canonical profile and resume intelligence.
2.  Role-driven discovery, data enrichment, and fitness scoring.
3.  Company intelligence and source resolution algorithms.
4.  Tailored document generation and PDF/Markdown export.
5.  Guarded application automation with granular diagnostics and OTP interception.

These subsystems operate under one strict product invariant: **The canonical candidate profile is the single trusted source of resume facts.**

## Domain Boundaries

### 1. Authentication and User Scope
*   Cookie-backed JWT session authentication flow.
*   Request-scoped IDs and structured logging integrated into API responses.
*   Rate-limiting enforced on authentication and inbox-sensitive endpoints.
*   Strict user-scoping for profiles, jobs, roles, companies, inbox connections, and application records.
*   **Key Routes**:
    *   `/auth/register`
    *   `/auth/login`
    *   `/auth/logout`
    *   `/auth/me`

### 2. Candidate Brain
*   File upload and text extraction supporting PDF, DOCX, and TXT formats.
*   Structured parsed sections: basics, summary, skills, experience, projects, education, certifications, and links.
*   `candidate_profiles` remains strictly fact-locked and authoritative.
*   The web profile editor facilitates section-based editing, crucial preferences, and saved answers.
*   Persistent profile settings govern automation thresholds, job filters, and resume rendering defaults.
*   A portable user-preference export provides configurations for external automation tooling.

### 3. Resume Themes, Templates, and Export
*   Includes three built-in ATS-safe light themes.
*   Structured input builder ensuring RenderCV compatibility.
*   Internal PDF fallback rendering system active if RenderCV encounters errors.
*   Packaged resume-template assets: `sections.json`, `resume_template.md`, `resume_template.tex`.
*   A localized CLI facilitates template listing, rendering, and PDF export testing.
*   The web resume UI exposes theme selection, template browsing, and live Markdown/LaTeX source previews.

### 4. Role-Driven Discovery and Enrichment
*   `target_roles` defines critical criteria: aliases, keywords, locations, remote preferences, salary targets, visa status, seniority, company inclusion/exclusion, and automation thresholds.
*   `target_role_sources` manages source subscriptions.
*   The packaged discovery registry supplies source presets, search templates, and blocked domain lists.
*   Ingestion is explicitly decoupled into: Initial Discovery -> Worker-Queued Enrichment -> Revision-Aware Scoring.
*   Job lifecycle events are tracked meticulously (discovered, enriched, score_changed, expired).

### 5. Company Intelligence
*   `companies` table provides canonical, user-scoped company identities.
*   `company_career_portals` stores provider-specific careers metadata.
*   `company_contacts` tracks recruiter and HR information independently of specific job postings.
*   Jobs utilize company heuristics to resolve structured data before defaulting to raw text retention.

### 6. Scoring and Tailoring
*   Scoring algorithms evaluate: canonical profile + target role + latest enrichment revision.
*   Score outputs detail: overall score, analytical breakdown, identified strengths, missing skills, transparent reasoning, and actionable recommendations.
*   Document tailoring preserves: matched requirements, uncovered requirements, emphasized experience/projects, and the specific source enrichment revision used.
*   Cover letters are generated dynamically and stored per job application.

### 7. Application Packets and Run Orchestration
*   `applications` represent the overarching job application record.
*   `application_runs` detail specific execution attempts.
*   `application_steps` store step-level evidence and metadata.
*   A preflight phase constructs a formal "application packet" prior to worker execution.
*   Packets contain resolved answers, data provenance, resume/cover-letter linkages, identified blocking issues, risk summaries, and auto-submit eligibility flags.
*   A formal Finite State Machine (FSM) governs transitions: `queued` -> `running` -> `paused` / `failed` / `completed` / `uncertain`.

### 8. Worker Execution and Persistence
*   The Celery worker interacts directly with the shared PostgreSQL database and file storage.
*   `RunRecorder` persists individual step rows and status modifications.
*   Screenshots are durably stored as `uploaded_files`.
*   `application_runs` internally persist retry and backoff histories.
*   The application runner supports:
    *   Page navigation and anti-bot detection.
    *   Common text fields, select, radio, checkbox, and date field adapters.
    *   Resume file uploads.
    *   Next/continue multi-step transitions.
    *   Unsupported required-field pause gates.
    *   Assisted pause-before-submit gates.
    *   Submit confirmation detection heuristics.

### 9. Inbox and OTP Integration
*   Native Gmail and Outlook OAuth integrations.
*   Provider readiness reporting surfaced within the UI.
*   Encrypted token storage ensuring sanitized API responses.
*   OTP retrieval supports: provider inbox fetch, manual message payload fallback, and masked event logging.
*   OTP extraction is treated as a first-class execution step in the FSM.

## Key Persistence Model

Primary PostgreSQL tables forming the data model:
*   `users`
*   `candidate_profiles`
*   `resumes`, `resume_versions`, `resume_themes`
*   `jobs`, `job_scores`, `job_sources`
*   `target_roles`, `target_role_sources`
*   `job_ingestion_runs`, `job_feed_events`
*   `companies`, `company_career_portals`, `company_contacts`
*   `cover_letters`
*   `applications`, `application_runs`, `application_steps`
*   `inbox_connections`, `inbox_otp_events`
*   `uploaded_files`
*   `settings`, `audit_logs`

## Main Runtime Flows

### Resume Flow
1.  Upload source resume.
2.  Extract raw text.
3.  Parse text into the structured canonical profile.
4.  Select desired theme or starter template.
5.  Generate tailored resume version.
6.  Export PDF via RenderCV-first fallback pipeline.

### Discovery Flow
1.  Create a target role.
2.  Attach packaged or manual source subscriptions.
3.  Execute discovery run.
4.  Insert or refresh normalized job records.
5.  Dispatch enrichment tasks per job to the worker queue.
6.  Record score metrics and append feed events.

### Apply Flow
1.  Prepare the structured application packet.
2.  Create a `queued` application run.
3.  Dispatch to the Celery worker.
4.  Persist steps, screenshots, and evaluation pauses.
5.  Request OTP via inbox connection if challenged.
6.  Transition via FSM to `pause`, `fail`, `complete`, or `uncertain`.

## Safety and Reliability Patterns

*   **Fact-Locked Tailoring**: Zero invented claims; outputs strictly repurpose verified profile facts.
*   **Explicit Approval Gates**: Risky questions trigger mandatory operator approval.
*   **Graceful Degradation**: Unknown answers default to candidate review requirements.
*   **Anti-Bot Compliance**: CAPTCHA and anti-bot challenges trigger a pause state rather than attempting bypass.
*   **Data Integrity**: Deduplication keys shield discovery routines from duplicate record insertion.
*   **Diagnostic Visibility**: Enrichment retry controls and run retry capabilities are exposed to operators.
*   **Traceability**: Request IDs and structured logs enhance API and worker debugging.
*   **Durable Evidence**: Worker evidence (screenshots, step logs) remains durable even following a partial process failure.
*   **Secret Masking**: Provider tokens and OTP values are actively masked or encrypted.

## Best File Entry Points

### Resume and Document Flows
*   `apps/api/app/services/resume_parser.py`
*   `apps/api/app/services/resume_themes.py`
*   `apps/api/app/services/resume_templates.py`
*   `apps/api/app/services/files.py`
*   `apps/api/app/api/routes/resume_templates.py`

### Discovery and Scoring
*   `apps/api/app/services/role_ingestion.py`
*   `apps/api/app/services/job_dispatch.py`
*   `apps/api/app/services/job_enrichment.py`
*   `apps/api/app/services/company_directory.py`
*   `apps/api/app/services/scoring.py`

### Automation and Preferences
*   `apps/api/app/services/application_packets.py`
*   `apps/api/app/services/application_fsm.py`
*   `apps/api/app/services/user_preferences.py`
*   `apps/api/app/api/routes/applications.py`
*   `apps/api/app/api/routes/application_runs.py`
*   `apps/worker/app/playwright_runner.py`
*   `apps/worker/app/persistence.py`
*   `apps/worker/app/run_fsm.py`

### UX Surfaces
*   `apps/web/app/resume/page.tsx`
*   `apps/web/app/jobs/page.tsx`
*   `apps/web/app/applications/page.tsx`
*   `apps/web/components/forms/settings-form.tsx`
*   `apps/web/app/companies/page.tsx`
*   `apps/web/app/wizard/page.tsx`

## Migration Note

The API currently invokes `create_all` during startup for local development convenience. In the long term, runtime schema creation should be deprecated in favor of strict, Alembic-only schema migrations.

## Verification Baseline

Before merging nontrivial architectural changes, ensure the following checks pass:

1.  `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2.  `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3.  `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4.  `npm run lint` (in `apps/web`)
5.  `npm run build` (in `apps/web`)
6.  `npm run typecheck` (in `apps/web` - safest after `build`)
