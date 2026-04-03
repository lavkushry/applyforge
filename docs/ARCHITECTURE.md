# System Architecture for ApplyForge

## High-Level Topology

ApplyForge is structured as a monorepo that encapsulates three primary runtime services and a centralized configuration layer:

1. **`apps/web`**
   - Built on the Next.js App Router.
   - Manages API data fetching and caching with TanStack Query.
   - Uses React Hook Form combined with Zod for robust client-side validation.
   - Relies on Zustand for managing lightweight global states (like sessions and toasts).

2. **`apps/api`**
   - A high-performance FastAPI backend.
   - Uses SQLAlchemy for relational database operations and ORM management.
   - Enforces strict data contracts using Pydantic models.
   - Houses deterministic core logic for resume parsing, document generation, job scoring, and system orchestration.

3. **`apps/worker`**
   - An asynchronous Celery task processor.
   - Integrates Playwright for complex browser automation.
   - Executes background job enrichment and heavy data processing.
   - Manages step-by-step application execution, capturing visual evidence (screenshots) and enforcing manual checkpoints.

4. **`packages/config`**
   - Stores the registry of discovery presets (sources and search queries).
   - Contains foundational resume templates and structural assets.
   - Designed to hold future standardized product defaults.

Additional contextual information is maintained in:
- The `docs` folder (architectural decisions, deployment procedures, and roadmaps).
- The `.agents/skills` folder (guidelines for AI agents regarding domain rules and operations).
- The `.codex/agents` folder (definitions for specific AI roles within the repository).

## Core Functional Subsystems

The platform is divided into five interrelated functional areas. The primary invariant across all of them is that the **user's canonical profile remains the sole, immutable source of truth for all resume facts.**

### 1. Authentication and Scope

- Utilizes secure, HTTP-only, cookie-based JWT sessions.
- Injects request-scoped correlation IDs into all API responses and structured logs for traceability.
- Implements strict rate-limiting on sensitive endpoints (e.g., authentication, inbox integration).
- Ensures rigid multi-tenant isolation; profiles, jobs, targets, companies, and application runs are strictly scoped to the authenticated user.
- Key endpoints include `/auth/register`, `/auth/login`, `/auth/logout`, and `/auth/me`.

### 2. The Candidate Profile Engine

- Handles file uploads (PDF, DOCX, TXT) and performs text extraction.
- Parses raw text into structured canonical sections: basics, summary, skills, experience, projects, education, certifications, and links.
- The resulting `candidate_profiles` records are locked to prevent factual drift.
- Provides a detailed UI for editing individual profile sections and maintaining critical automation preferences (e.g., visa status, salary requirements).
- Consolidates settings for job filtering and resume rendering, and provides a portable configuration export for operators.

### 3. Document Generation and Export

- Ships with three native, ATS-optimized light resume themes.
- Generates structured JSON payloads compatible with RenderCV for high-fidelity PDF rendering.
- Includes an internal PDF generation fallback to guarantee availability if RenderCV execution fails.
- Maintains static template definitions in `packages/config/resume/`.
- Features a developer CLI for testing template rendering and exporting PDFs locally.
- Provides an interactive web UI allowing users to preview their canonical data in different visual themes before export.

### 4. Job Discovery and Enrichment Pipeline

- Relies on `target_roles` to dictate user strategy, including desired keywords, locations, remote status, compensation, and automation thresholds.
- Tracks `target_role_sources` to manage active subscriptions to job boards or employer career pages.
- Leverages a preset registry to rapidly configure complex search queries and filter out blocked domains.
- Decouples operations into three distinct phases: initial discovery, asynchronous enrichment (via the worker), and revision-based scoring.
- Exposes a realtime feed mapping the lifecycle of a job: discovered -> enriched -> score altered -> expired.

### 5. Company Intelligence Directory

- Maintains user-specific `companies` records to normalize employer data.
- Uses `company_career_portals` to track ATS entry points and provider metadata.
- Stores `company_contacts` to associate recruiters and HR personnel with specific organizations.
- Employs heuristic matching to resolve raw scraped job text to established company directory records, improving data cleanliness.

### 6. Scoring and Tailoring Logic

- Generates match scores by evaluating the enriched job data against the user's canonical profile and the active target role strategy.
- Outputs detailed score breakdowns, highlighting strengths, missing skills, and overall recommendations.
- Drives the tailoring process to specifically emphasize relevant experience and summarize qualifications matching the job description.
- Preserves transparency by tracking exactly which job enrichment revision was used to generate a tailored resume or cover letter.

### 7. Orchestration and Application Packets

- Organizes data into `applications` (the high-level intent) and `application_runs` (the specific execution attempt).
- Compiles a "preflight" application packet before a run begins, encompassing resolved answers, linked documents, identified risks, and auto-submit eligibility.
- Manages execution state through a rigorous Finite State Machine (FSM) enforcing transitions between `queued`, `running`, `paused`, `failed`, `completed`, and `uncertain`.
- Records atomic `application_steps` to maintain an audit trail of the process.

### 8. Worker Execution Engine

- Tasks are executed by the worker, directly writing state back to the shared database and artifact storage.
- Utilizes a `RunRecorder` to document granular step progress and status shifts.
- Captures and stores Playwright screenshots as `uploaded_files` linked to specific application steps.
- Supports a variety of interactive web operations: navigation, dynamic field filling (text, selects, checkboxes), document uploads, and anti-bot detection.
- Enforces strict execution pauses when encountering unsupported fields, risky questions, or when transitioning to a final submission review.

### 9. Inbox Integration and OTPs

- Facilitates OAuth connections with Google (Gmail) and Microsoft (Outlook) for automated One-Time Password retrieval.
- Displays real-time configuration readiness in the web interface.
- Stores provider tokens securely, ensuring API responses never leak raw credentials.
- Automates the lookup of OTPs during application flows, masking the sensitive codes in logs, and gracefully degrading to manual user input if retrieval fails.

## Data Persistence Strategy

The system relies on a unified PostgreSQL schema containing several core tables:

**Users & Identity:** `users`, `inbox_connections`, `settings`
**Candidate Data:** `candidate_profiles`, `resumes`, `resume_versions`, `resume_themes`, `cover_letters`
**Job Intelligence:** `jobs`, `job_scores`, `job_sources`, `target_roles`, `target_role_sources`, `job_ingestion_runs`, `job_feed_events`
**Company Directory:** `companies`, `company_career_portals`, `company_contacts`
**Execution & Audit:** `applications`, `application_runs`, `application_steps`, `inbox_otp_events`, `uploaded_files`, `audit_logs`

## Primary System Workflows

### The Resume Pipeline
1. Ingest the source file (PDF/DOCX/TXT).
2. Extract text and parse into a structured canonical profile.
3. User selects a visual theme or LaTeX starter.
4. The system produces a job-specific tailored variant.
5. Render and export the final ATS-friendly PDF.

### The Discovery Pipeline
1. User defines a target role strategy.
2. User attaches data sources (manual or presets).
3. The system executes discovery scraping.
4. Ingested jobs are normalized and deduplicated.
5. Jobs are dispatched to the worker for deep enrichment.
6. The system recalculates scores and updates the event feed.

### The Application Pipeline
1. The API compiles an application packet (data, files, risk assessment).
2. A new run is initialized and queued.
3. The Celery worker picks up the run and launches Playwright.
4. The worker navigates the application, persisting steps, screenshots, and enforcing required pauses.
5. The system requests and retrieves an OTP if necessary.
6. The FSM manages the final disposition (complete, failed, or paused for review).

## Operational Safety Measures

- **Truth Constraints**: Tailoring logic is heavily prompted to prevent the fabrication of skills or experience.
- **Human in the Loop**: Any question flagged as risky automatically forces a manual review pause.
- **Degradation**: If the system cannot answer a prompt, it defers to the user rather than guessing.
- **Anti-Bot Respect**: Workflows will pause rather than attempt to subvert CAPTCHAs or advanced security challenges.
- **Deduplication**: Robust hashing prevents the database from bloating with duplicate job postings across different sources.
- **Artifact Retention**: Playwright screenshots and run histories remain intact even if a run crashes, ensuring post-mortem diagnostics are always available.

## Navigating the Codebase

### Document & Resume Operations
- Parsing logic: `apps/api/app/services/resume_parser.py`
- Theme handling: `apps/api/app/services/resume_themes.py`
- Template generation: `apps/api/app/services/resume_templates.py`
- Export and file management: `apps/api/app/services/files.py`
- Web view: `apps/web/app/resume/page.tsx`

### Discovery & Scoring
- Ingestion orchestrator: `apps/api/app/services/role_ingestion.py`
- Enrichment queues: `apps/api/app/services/job_dispatch.py` & `apps/api/app/services/job_enrichment.py`
- Company resolution: `apps/api/app/services/company_directory.py`
- Match logic: `apps/api/app/services/scoring.py`

### Automation & State Machine
- Packet building: `apps/api/app/services/application_packets.py`
- State enforcement: `apps/api/app/services/application_fsm.py`
- Worker entry point: `apps/worker/app/playwright_runner.py`
- Worker state management: `apps/worker/app/run_fsm.py` & `apps/worker/app/persistence.py`

## Schema Migration Status

The API currently leverages `Base.metadata.create_all(...)` during startup to accommodate rapid MVP iterations. Moving forward, this will be deprecated in favor of rigorous Alembic migrations.

## Code Quality and Verification

Before submitting significant architectural or functional modifications, execute the standard verification loop:

1. Validate Python syntax: `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. Run backend tests: `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. Run worker tests (with in-memory DB mocks): `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. Lint frontend code: `npm run lint` (in `apps/web`)
5. Build frontend codebase: `npm run build` (in `apps/web`)
6. Check frontend types: `npm run typecheck` (in `apps/web`)
