# ApplyForge Architectural Overview

## System Layout

The ApplyForge monorepo consists of three core applications and a shared configuration package:

- **Frontend (`apps/web`)**: A Next.js (App Router) client using TanStack Query for state, React Hook Form for data entry, and Zustand for toast notifications and session management.
- **Backend API (`apps/api`)**: A FastAPI-based service backed by PostgreSQL and SQLAlchemy, handling REST operations, deterministic job processing, resume parsing, and application prep.
- **Background Worker (`apps/worker`)**: A Celery distributed worker leveraging Playwright for intelligent application fulfillment, screenshot capturing, and web interactions.
- **Configurations (`packages/config`)**: Stores baseline templates (like RenderCV themes) and discovery logic.

Documentation lives under `docs/`, while AI agent guidelines reside in `.agents/skills` and `.codex/agents`.

## Domain Capabilities

1. **Identity & Auth**: JWT cookie sessions provide user-scoped isolation for jobs, resumes, inbox, and applications.
2. **Profile & Resume Brain**: Parses PDFs/DOCX files into an immutable structured profile. Includes standard fields like Experience, Education, and Skills.
3. **Template Export Engine**: Packages ATS-optimized resume themes rendered via a RenderCV fallback pipeline into valid PDFs.
4. **Job Ingestion & Discovery**: Aggregates job feeds based on customizable user targets. Processes job discovery, queuing, and expiration gracefully.
5. **Company Tracking**: Maps job roles to standardized company identities, career portals, and potential HR contacts.
6. **Smart Tailoring**: Matches user profiles against job descriptions to create custom scoring heuristics, tailored bullet points, and dynamic cover letters.
7. **Execution Control (FSM)**: Manages end-to-end applications through rigorous finite-state machine states (queued, running, paused, failed, completed). Includes strict diagnostics and bot checks.
8. **Worker Execution**: Celery tasks run durable scraping routines, recording steps, visual evidence (screenshots), and runtime artifacts direct to database and file storage.
9. **Inbox Integration**: Securely integrates with Gmail and Outlook via OAuth to automatically extract One-Time Passwords (OTPs) needed to bypass application verification flows.

## Persistence Stack

Core tables include `users`, `candidate_profiles`, `resumes`, `jobs`, `target_roles`, `applications`, `inbox_connections`, and `uploaded_files`.

## Baseline Safety Guarantees

- System never fabricates non-existent profile facts.
- Ambiguous questions mandate manual human fallback (pausing the FSM).
- Bot detection stops flows automatically instead of risking ghost bans.
- Token data stays heavily masked.

## Critical Paths & Verifications

Primary services are distributed across `apps/api/app/services` (e.g., `resume_parser.py`, `job_enrichment.py`, `application_packets.py`) and `apps/worker/app` (e.g., `playwright_runner.py`).

To ensure continuous operation:
1. `make lint`
2. `make web-typecheck`
3. `make api-test`