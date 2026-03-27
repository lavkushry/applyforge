# ApplyForge Architecture

## High-Level
- **Web (Next.js)** handles UX, forms, dashboard, and run monitoring.
- **API (FastAPI)** owns business logic, auth, persistence, scoring, tailoring orchestration.
- **Worker (Celery + Playwright)** executes long-running tasks and application automation flows.
- **PostgreSQL** stores normalized entities and immutable run logs.
- **Redis** provides queue transport and lightweight caching.

## Core Domains
- Identity/Auth
- Candidate Resume Brain
- Job Ingestion & Scoring
- Tailoring & Cover Letter Generation
- Application Automation & Run Timeline
- Diagnostics / Admin

## Reliability Patterns
- Idempotent job imports via URL/content hash.
- Step-based automation state (`application_steps`) with retries.
- Structured errors with user-safe messages.
- Prompt metadata logging with masked sensitive fields.

## AI Layer
Prompts live in `packages/prompts`. API service wrappers consume prompts and an OpenAI-compatible client abstraction.
