# ApplyForge Architecture

## System Overview

ApplyForge is structured as a monorepo featuring three core runtime applications alongside a configuration layer:

1. **`apps/web`**
   - Frontend powered by Next.js App Router.
   - TanStack Query for managing API state.
   - React Hook Form and Zod for robust form handling.
   - Zustand for managing session and toast states.

2. **`apps/api`**
   - Backend service built with FastAPI.
   - SQLAlchemy ORM models ensuring reliable data persistence.
   - Pydantic schemas validating request and response contracts.
   - Deterministic-first services managing scoring, tailoring, parsing, exporting, and orchestration.

3. **`apps/worker`**
   - Celery worker paired with a Playwright runtime.
   - Handles job enrichment execution.
   - Orchestrates step-based applications, reliably preserving screenshots and handling pause gates.

4. **`packages/config`**
   - Houses the discovery preset registry.
   - Contains resume template assets.
   - Serves as the future repository for additional packaged product defaults.

**Supporting Artifacts:**
- `docs/`: Product, architecture, and roadmap documentation.
- `.agents/skills/`: Domain and operations guidance specific to ApplyForge.
- `.codex/agents/`: Definitions for project-local Codex roles.

## Current Architectural Shape

ApplyForge operates across five deeply interconnected subsystems:

1. Canonical profile and resume intelligence.
2. Role-driven discovery, enrichment, and scoring.
3. Company intelligence and source resolution.
4. Tailored document generation and export.
5. Guarded application automation, featuring extensive diagnostics and OTP support.

**Product Invariant:** The canonical candidate profile always serves as the sole, trusted source of truth for resume facts.

## Domain Boundaries

### 1. Authentication & User Scope
- Secure cookie-backed JWT session flows.
- API responses include request-scoped IDs and structured logs.
- Strict rate limiting on authentication and inbox-sensitive endpoints.
- User-scoped isolation for profiles, jobs, roles, companies, inbox connections, and applications.
- **Core Routes:** `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/me`.

### 2. Candidate Brain
- Text extraction handling PDF, DOCX, and TXT file uploads.
- Parses core sections: basics, summary, skills, experience, projects, education, certifications, and links.
- `candidate_profiles` remains authoritative and fact-locked.
- The web profile editor supports section-based editing and managing apply-critical preferences/saved answers.
- Profile settings securely persist automation preferences, job filters, and resume preferences.
- A portable user-preference export caters to operators and future automation tooling.

### 3. Resume Themes, Templates & Export
- Three built-in, ATS-safe light themes.
- RenderCV-compatible structured input builder with an internal PDF fallback renderer.
- **Packaged Assets:** `packages/config/resume/sections.json`, `packages/config/resume/resume_template.md`, `packages/config/resume/resume_template.tex`.
- A dedicated CLI facilitates template listing, rendering, and PDF export.
- The web interface supports theme selection, template browsing, and live Markdown/LaTeX previews.

### 4. Role-Driven Discovery & Enrichment
- `target_roles` define aliases, keywords, locations, remote preferences, salary, visa needs, seniority, company filters, and automation thresholds.
- `target_role_sources` manage source subscriptions.
- The packaged discovery registry offers source presets, search templates, and blocked domains.
- Ingestion systematically splits into discovery, worker-queued enrichment, and revision-aware scoring.
- Job lifecycles are tracked via feed events: discovered, enriched, score_changed, expired.

### 5. Company Intelligence
- `companies` establishes canonical, user-scoped company identities.
- `company_career_portals` securely preserve provider-specific careers metadata.
- `company_contacts` manage recruiter and HR context independently from job records.
- Jobs resolve via company heuristics before defaulting to raw text.

### 6. Scoring & Tailoring
- Scoring evaluates the canonical profile, target role, and enrichment revisions.
- Score outputs break down overall scores, strengths, missing skills, reasons, and recommendations.
- Tailoring meticulously preserves matched/uncovered requirements, and dynamically emphasizes experience/projects while tracking the source enrichment revision.
- Job-specific cover letters are actively generated and stored.

### 7. Application Packets & Run Orchestration
- `applications` track job-level application records.
- `application_runs` log execution attempts.
- `application_steps` capture granular, step-level evidence.
- Preflight routines assemble a formal application packet pre-execution, containing: resolved answers, provenance, resume/cover-letter links, blocking issues, risk summaries, and auto-submit eligibility.
- A formal FSM governs run transitions: `queued`, `running`, `paused`, `failed`, `completed`, `uncertain`.

### 8. Worker Execution & Persistence
- Workers write directly to shared database and file storage.
- `RunRecorder` reliably persists step rows and status updates.
- Screenshots are saved as `uploaded_files`.
- Application runs persist retry and backoff history directly.
- The application runner supports navigation, common text/select fields, resume uploads, anti-bot detection, and pause-before-submit workflows.

### 9. Inbox & OTP
- Built-in Gmail and Outlook OAuth integrations.
- UI explicitly reports provider readiness.
- Secure, encrypted token storage with sanitized API responses.
- OTP retrieval natively supports provider inbox fetching and manual message fallbacks, ensuring masked event logging.
- OTP retrieval functions as a first-class run step.

## Key Persistence Model

**Primary Tables:**
- `users`, `candidate_profiles`, `resumes`, `resume_versions`, `resume_themes`
- `jobs`, `job_scores`, `job_sources`, `target_roles`, `target_role_sources`
- `job_ingestion_runs`, `job_feed_events`
- `companies`, `company_career_portals`, `company_contacts`
- `cover_letters`, `applications`, `application_runs`, `application_steps`
- `inbox_connections`, `inbox_otp_events`, `uploaded_files`, `settings`, `audit_logs`

## Main Runtime Flows

### Resume Flow
1. Upload source resume.
2. Extract raw text.
3. Parse into the canonical profile.
4. Select a theme or starter template.
5. Generate a tailored version.
6. Export the PDF via the RenderCV-first fallback pipeline.

### Discovery Flow
1. Create a target role.
2. Attach packaged or manual sources.
3. Run discovery.
4. Insert/refresh normalized jobs.
5. Dispatch enrichment per job.
6. Write score and feed events.

### Apply Flow
1. Prepare application packet.
2. Create queued run.
3. Dispatch worker.
4. Persist steps, screenshots, and pauses.
5. Request OTP (if needed).
6. Transition FSM states (pause, fail, complete, or uncertain).

## Safety & Reliability Patterns

- Fact-locked tailoring strictly prevents invented claims.
- Explicit approval gates manage risky questions.
- Unknown answers purposefully degrade to require candidate review.
- CAPTCHA and anti-bot flows default to pause rather than attempting bypasses.
- Deduplication keys shield discovery from duplicate insertions.
- Diagnostics clearly expose retry and run controls.
- Request IDs and structured logs ensure robust API/worker traceability.
- Run history reliably exposes screenshot evidence and retry metadata.
- Tokens and OTPs remain perpetually masked or encrypted.
- Worker evidence is durably preserved even after partial failures.

## Best File Entry Points

### Resume & Document Flows
- `apps/api/app/services/resume_parser.py`
- `apps/api/app/services/resume_themes.py`
- `apps/api/app/services/resume_templates.py`
- `apps/api/app/services/files.py`
- `apps/api/app/api/routes/resume_templates.py`

### Discovery & Scoring
- `apps/api/app/services/role_ingestion.py`
- `apps/api/app/services/job_dispatch.py`
- `apps/api/app/services/job_enrichment.py`
- `apps/api/app/services/company_directory.py`
- `apps/api/app/services/scoring.py`

### Automation & Preferences
- `apps/api/app/services/application_packets.py`
- `apps/api/app/services/application_fsm.py`
- `apps/api/app/services/user_preferences.py`
- `apps/api/app/api/routes/applications.py`
- `apps/api/app/api/routes/application_runs.py`
- `apps/worker/app/playwright_runner.py`
- `apps/worker/app/persistence.py`
- `apps/worker/app/run_fsm.py`

### UX Surfaces
- `apps/web/app/resume/page.tsx`
- `apps/web/app/jobs/page.tsx`
- `apps/web/app/applications/page.tsx`
- `apps/web/components/forms/settings-form.tsx`
- `apps/web/app/companies/page.tsx`
- `apps/web/app/wizard/page.tsx`

## Migration Note

The API currently executes `create_all` at startup for local MVP convenience. Future updates will remove runtime schema creation, fully delegating database management to Alembic migrations.

## Verification Baseline

For nontrivial changes, ensure the following checks pass:

1. `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. `npm run lint` in `apps/web`
5. `npm run build` in `apps/web`
6. `npm run typecheck` in `apps/web`

*Note: In this repo, `typecheck` is safest after `build` since `tsconfig.json` includes `.next/types`.*
