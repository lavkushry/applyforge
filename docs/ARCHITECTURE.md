# ApplyForge System Architecture

## Repository Structure
ApplyForge is structured as a monorepo containing three primary services and a shared configuration library:

1. **Frontend (`apps/web`)**
   - Framework: Next.js App Router
   - State Management: TanStack Query (API), Zustand (Session/UI)
   - Forms: React Hook Form + Zod

2. **Backend API (`apps/api`)**
   - Framework: FastAPI
   - Database: SQLAlchemy ORM
   - Validation: Pydantic schemas
   - Role: Manages core orchestration, parsing, scoring, and data serving.

3. **Task Worker (`apps/worker`)**
   - Framework: Celery
   - Engine: Playwright
   - Role: Executes asynchronous job enrichment and manages step-by-step browser automation for job applications.

4. **Shared Configuration (`packages/config`)**
   - Houses domain presets, blocklists, and resume template assets.

*Additional contextual documentation can be found in `docs/`, `.agents/skills/`, and `.codex/`.*

## Core Subsystems
The application is divided into five logical domains, all adhering to the strict rule that the **Candidate Profile is the sole source of truth**.

### 1. Identity & Session Management
- Utilizes secure, HTTP-only JWT cookies.
- Implements structured, request-scoped logging and rate limiting.
- Enforces strict user-level isolation for all profile, job, and application data.

### 2. Profile Intelligence
- Ingests resumes (PDF/DOCX/TXT) to extract structured text.
- Segments data into Experience, Education, Skills, and Projects.
- Exposes granular editing via the web UI and stores configuration preferences for future automation tools.

### 3. Resume Generation
- Offers multiple ATS-compliant light themes.
- Compiles structured data into Markdown or LaTeX templates (RenderCV compatible).
- Employs a reliable internal PDF rendering fallback to guarantee export stability.

### 4. Discovery & Scoring Engine
- "Target Roles" govern search queries, locations, salary expectations, and thresholds.
- A background pipeline handles discovery, queues jobs for worker enrichment, and applies version-aware scoring algorithms.
- Maintains a detailed feed of job lifecycle events (discovered, enriched, expired).

### 5. Application Execution FSM
- Compiles "Application Packets" containing locked facts, generated cover letters, and blockage risk assessments prior to execution.
- Orchestrates runs through a strict Finite State Machine (Queued -> Running -> Paused -> Completed/Failed).
- The worker writes execution evidence (screenshots, field logs) directly to persistent storage to survive sudden crashes.
- Integrates with Gmail/Outlook OAuth for automated OTP retrieval during complex login flows.

## Entity Relationship Overview
Key database tables include:
- **Identity:** `users`, `candidate_profiles`, `settings`
- **Documents:** `resumes`, `resume_versions`, `resume_themes`, `cover_letters`
- **Discovery:** `target_roles`, `job_sources`, `jobs`, `job_scores`, `companies`
- **Execution:** `applications`, `application_runs`, `application_steps`, `uploaded_files`, `inbox_otp_events`

## Execution Pipelines
- **Resume Generation:** Upload -> Parse -> Map to Profile -> Apply Theme -> Generate PDF.
- **Job Discovery:** Define Role -> Poll Sources -> Save Job -> Trigger Enrichment -> Compute Score.
- **Application Automation:** Build Packet -> Dispatch Task -> Playwright Execution -> Log Steps/Screenshots -> Await OTP/Completion.

## Operational Guardrails
- **Zero Hallucination:** Tailoring relies entirely on established profile facts.
- **Manual Oversight:** Ambiguous questions or CAPTCHAs pause the FSM for human intervention.
- **Deduplication:** Strict database constraints prevent overlapping job ingestion.
- **Traceability:** Request IDs are carried through the stack, and worker actions are heavily logged for operator review.

## Important Code Boundaries

### Document Processing
- [resume_parser.py](../apps/api/app/services/resume_parser.py)
- [resume_themes.py](../apps/api/app/services/resume_themes.py)
- [resume_templates.py](../apps/api/app/services/resume_templates.py)

### Logic & Scoring
- [job_dispatch.py](../apps/api/app/services/job_dispatch.py)
- [job_enrichment.py](../apps/api/app/services/job_enrichment.py)
- [scoring.py](../apps/api/app/services/scoring.py)

### Task Orchestration
- [application_packets.py](../apps/api/app/services/application_packets.py)
- [application_fsm.py](../apps/api/app/services/application_fsm.py)
- [playwright_runner.py](../apps/worker/app/playwright_runner.py)
- [run_fsm.py](../apps/worker/app/run_fsm.py)

### Frontend Integration
- [resume/page.tsx](../apps/web/app/resume/page.tsx)
- [jobs/page.tsx](../apps/web/app/jobs/page.tsx)
- [wizard/page.tsx](../apps/web/app/wizard/page.tsx)

## Testing Mandate
For all substantial architectural modifications, execute:
1. Syntax verification: `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. API Unit Tests: `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. Worker Unit Tests: `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. Frontend Checks: `npm run lint`, `npm run build`, and `npm run typecheck` inside `apps/web`.
