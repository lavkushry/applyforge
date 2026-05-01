# ApplyForge Architecture

## 🏛️ System Overview

ApplyForge is designed as a modern monorepo comprising three distinct runtime applications supported by a centralized configuration package:

1. **`apps/web`**
   - **Framework:** Next.js App Router (Frontend)
   - **Data Fetching:** TanStack Query for robust API state management.
   - **Forms:** React Hook Form coupled with Zod for strict validation.
   - **State Management:** Zustand handling session and ephemeral toast states.

2. **`apps/api`**
   - **Framework:** FastAPI (Backend Service)
   - **Persistence:** SQLAlchemy ORM models interacting with PostgreSQL.
   - **Contracts:** Pydantic schemas strictly defining request and response payloads.
   - **Core Logic:** Deterministic-first domain services handling scoring, document tailoring, parsing, exporting, and overall orchestration.

3. **`apps/worker`**
   - **Task Queue:** Celery worker leveraging Redis.
   - **Automation:** Playwright runtime for browser interactions.
   - **Execution:** Handles background job enrichment and executes step-based application runs complete with durable screenshot captures and controlled pause gates.

4. **`packages/config`**
   - **Registry:** Contains discovery preset registries.
   - **Assets:** Houses baseline resume template assets.
   - **Future:** Designed to hold an expanding set of packaged product defaults.

**Contextual Artifacts:**
- **`docs/`**: Product specs, architectural decisions, and roadmap documentation.
- **`.agents/skills/`**: ApplyForge-specific domain knowledge and operational guidance for AI agents.
- **`.codex/agents/`**: Project-local Codex agent role definitions.

---

## 🧩 Current Architectural Shape

ApplyForge operates through five deeply interconnected subsystems:

1. **Canonical Intelligence:** Management of the authoritative candidate profile and base resume data.
2. **Role-Driven Pipeline:** Job discovery, data enrichment, and algorithmic scoring based on target roles.
3. **Corporate Intelligence:** Company directory resolution, portal mapping, and source context.
4. **Document Generation:** Tailored resume and cover letter generation with high-fidelity export mechanisms.
5. **Guarded Execution:** Step-based application automation featuring diagnostic captures, OTP retrieval, and strict state management.

**Core Invariant:** The canonical candidate profile remains the single, unalterable source of truth for all factual resume generation.

---

## 🛑 Domain Boundaries

### 1. Authentication and User Scope
- **Session Flow:** Secure, cookie-backed JWT implementation.
- **Traceability:** Request-scoped IDs and structured JSON logging applied to all API responses.
- **Protection:** Strict rate-limiting enforced on authentication and inbox-sensitive endpoints.
- **Isolation:** All major entities (profiles, jobs, roles, companies, inbox connections, applications) are strictly user-scoped.
- **Primary Routes:** `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`

### 2. Candidate Brain (Profile Core)
- **Ingestion:** Upload and text extraction engines for PDF, DOCX, and TXT formats.
- **Structured Parsing:** Transforms raw text into segmented sections (Basics, Summary, Skills, Experience, Projects, Education, Certifications, Links).
- **Authority:** `candidate_profiles` acts as the fact-locked anchor.
- **Editor:** The web profile editor supports granular, section-based editing and captures apply-critical preferences/saved answers.
- **Preferences:** Dedicated settings management for automation thresholds, job filters, and resume preferences, culminating in a portable user-preference export tool.

### 3. Resume Themes, Templates, and Export
- **Themes:** Ships with three built-in ATS-safe light themes.
- **Generation:** Utilizes a RenderCV-compatible structured input builder, backed by an internal PDF fallback renderer ensuring export continuity.
- **Assets:** Packaged templates include `sections.json`, `resume_template.md`, and `resume_template.tex`.
- **Tooling:** A local CLI (`app.cli.main`) facilitates template listing and PDF rendering tests.
- **Web Interface:** Users can browse templates, select themes, and preview rendered Markdown or LaTeX source code prior to export.

### 4. Role-Driven Discovery and Enrichment
- **Strategy (`target_roles`):** Defines the core search logic (aliases, keywords, location/remote preferences, compensation targets, visa needs, company block/allow lists, and auto-apply thresholds).
- **Sources (`target_role_sources`):** Manages active source subscriptions.
- **Registry:** Packaged configurations supply ready-to-use presets and blocked domains.
- **Lifecycle:** The ingestion pipeline is explicitly split into *Discovery*, *Worker-Queued Enrichment*, and *Revision-Aware Scoring*.
- **Feed Events:** Job states are durably tracked via feed events (`discovered`, `enriched`, `score_changed`, `expired`).

### 5. Company Intelligence
- **Identity (`companies`):** Provides a canonical, user-scoped company identifier.
- **Portals (`company_career_portals`):** Preserves specific career site metadata (ATS providers, board tokens).
- **Contacts (`company_contacts`):** Independently tracks recruiters and HR personnel.
- **Resolution:** Newly discovered jobs utilize heuristic matching to map against known companies prior to falling back to free-text strings.

### 6. Scoring and Tailoring
- **Scoring Engine:** Evaluates fit based on the canonical profile, the active target role, and the latest enrichment revision.
- **Transparency:** Outputs detailed metrics including an overall score, categorical breakdowns, identified strengths, missing requirements, explicit reasons, and an ultimate recommendation.
- **Tailoring Constraints:** Generation preserves and highlights matched requirements while identifying gaps. It emphasizes relevant experience and projects without hallucinating data.
- **Ancillary Documents:** Cover letters are dynamically generated and durably stored per job application.

### 7. Application Packets and Orchestration
- **Data Model:** `applications` (the core record), `application_runs` (execution attempts), and `application_steps` (granular evidence).
- **Preflight (`application_packets`):** Assembles a formalized packet *before* execution, bundling resolved answers, data provenance, linked resume/cover letters, known blocking issues, risk assessments, and auto-submit eligibility flags.
- **State Machine (FSM):** Governs strict run transitions: `queued` → `running` → (`paused` | `failed` | `completed` | `uncertain`).

### 8. Worker Execution and Persistence
- **Architecture:** Celery workers write directly to the shared PostgreSQL database and file storage.
- **Evidence:** The `RunRecorder` captures step-by-step progress and status changes. Browser screenshots are persisted as `uploaded_files`.
- **Resilience:** Application runs store retry/backoff metadata directly on the run record.
- **Capabilities:** The Playwright runner currently handles navigation, standard input fields (text, select, radio, checkbox, date), file uploads, simple multi-step pagination, anti-bot detection pauses, required-field gate pauses, assisted submit pauses, and success confirmation heuristics.

### 9. Inbox and OTP Integration
- **Providers:** Native OAuth integrations for Google (Gmail) and Microsoft (Outlook).
- **Security:** Tokens are encrypted at rest; API payloads are sanitized.
- **Functionality:** Supports automated inbox fetching of OTP codes, falling back to manual entry if required. Events are masked to prevent secret leakage in logs.
- **Integration:** OTP retrieval operates as a first-class step within the application run timeline.

---

## 🗄️ Key Persistence Model

The core PostgreSQL tables driving the system:

- `users`, `settings`, `audit_logs`
- `candidate_profiles`, `resumes`, `resume_versions`, `resume_themes`
- `jobs`, `job_scores`, `job_sources`
- `target_roles`, `target_role_sources`
- `job_ingestion_runs`, `job_feed_events`
- `companies`, `company_career_portals`, `company_contacts`
- `cover_letters`, `applications`, `application_runs`, `application_steps`
- `inbox_connections`, `inbox_otp_events`
- `uploaded_files`

---

## 🔄 Main Runtime Flows

### 1. Resume Onboarding Flow
1. User uploads a source resume document.
2. System extracts raw text.
3. Parser structures the text into a canonical profile.
4. User selects an ATS-friendly theme or starter template.
5. System generates a tailored variant based on the canonical data.
6. Export pipeline triggers the RenderCV-first PDF generation (with internal fallback).

### 2. Discovery and Feed Flow
1. User defines a target role strategy.
2. User attaches packaged presets or manual source URLs.
3. Scheduled discovery workers scrape job headers.
4. System inserts deduplicated, normalized job records.
5. Enrichment tasks are dispatched to the Celery worker queue per job.
6. Enriched jobs are scored, generating score outputs and feed events for the UI.

### 3. Application Execution Flow
1. System compiles a comprehensive preflight application packet.
2. A new `queued` run is created via the FSM.
3. Celery dispatches the run to the Playwright worker.
4. Worker executes steps, continuously persisting logs, screenshots, and pauses.
5. System seamlessly requests OTPs via the Inbox integration if challenged.
6. The FSM transitions the run to `completed`, `paused`, `failed`, or `uncertain` based on the outcome.

---

## 🛡️ Safety and Reliability Patterns

- **Truth-Locked Generation:** Tailoring engines are strictly barred from inventing claims.
- **Approval Gates:** Risk-flagged questions (e.g., legal, salary) always force a manual approval pause.
- **Graceful Degradation:** Unknown answers default to a "candidate review" state rather than hallucinated text.
- **Anti-Bot Compliance:** Encounters with CAPTCHAs or bot challenges immediately pause the run rather than attempting evasion.
- **Idempotency:** Deduplication keys protect the discovery pipeline from double-inserting records.
- **Observability:** Diagnostic panels expose worker retry controls, run histories, and screenshot evidence to human operators.
- **Sanitization:** Provider tokens and OTP values are aggressively masked or encrypted before logging.
- **Durable Evidence:** Worker step logs and screenshots remain accessible even if the overall run fails midway.

---

## 📍 Best File Entry Points

If you need to quickly orient yourself within specific sub-systems, start here:

**Resume and Document Flows:**
- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`
- `apps/api/app/services/files.py`
- `apps/api/app/api/routes/resume_templates.py`

**Discovery and Scoring:**
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/company_directory.py`
- `apps/api/app/services/scoring.py`

**Automation and Preferences:**
- `apps/api/app/services/application_packets.py`
- `apps/api/app/services/application_fsm.py`
- `apps/api/app/services/user_preferences.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/persistence.py`
- `apps/worker/app/run_fsm.py`

**Primary UX Surfaces:**
- `apps/web/app/resume/page.tsx`
- `apps/web/app/jobs/page.tsx`
- `apps/web/app/applications/page.tsx`
- `apps/web/app/wizard/page.tsx`
- `apps/web/components/forms/settings-form.tsx`

---

## ⚠️ Migration Note

- *Technical Debt:* The API currently invokes `Base.metadata.create_all` during startup for local MVP convenience.
- *Future Work:* Runtime schema creation must be phased out entirely in favor of strict Alembic-only migrations before production release.

---

## ✅ Verification Baseline

Before opening a PR with nontrivial changes, verify system health by executing the following baseline commands from the repository root:

1. **Compile Python:**
   `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. **Test API:**
   `PYTHONPATH=/tmp/applyforge-pydeps:$(pwd)/apps/api python3 -m pytest apps/api/tests -q`
3. **Test Worker:**
   `PYTHONPATH=/tmp/applyforge-pydeps:$(pwd)/apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. **Lint Frontend:**
   `cd apps/web && pnpm lint`
5. **Build Frontend:**
   `cd apps/web && pnpm build`
6. **Typecheck Frontend:**
   `cd apps/web && pnpm typecheck` *(Note: In this repo, `typecheck` is safest after `build` because `tsconfig.json` relies on generated `.next/types`.)*