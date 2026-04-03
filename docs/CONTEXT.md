# Context & Orientation Guide for ApplyForge

This document serves as a rapid onboarding tool to help you understand the core objectives and current state of the ApplyForge monorepo, minimizing time spent re-discovering established patterns.

## The Core Product Loop

ApplyForge is designed as a cohesive operating system for job seekers, orchestrating five distinct phases of the job hunt:

1. **Profile Intelligence**: Establishing and maintaining a single, canonical repository of a candidate's verified skills and experience.
2. **Targeted Discovery**: Continuously scanning configured sources for roles, extracting metadata, and enriching job descriptions.
3. **Assessment & Tailoring**: Transparently scoring roles against the candidate profile and generating targeted, factually accurate resumes.
4. **Automated Execution**: Using a guarded, browser-based worker to navigate application forms while requiring human approval for complex or sensitive fields.
5. **Review & Diagnostics**: Providing deep visibility into application runs via screenshots, step logs, and OTP (One-Time Password) retrieval audits.

## Current Technical Maturity

The platform is actively functional and currently implements:

- A robust authentication layer using cookie-backed JWTs.
- Full text parsing and structural extraction from uploaded resumes.
- A built-in catalog of ATS-friendly resume themes and developer-oriented LaTeX/Markdown starter templates.
- A PDF generation pipeline leveraging RenderCV, backed by an internal renderer for high availability.
- A role registry that drives both job discovery schedules and automation logic.
- An intuitive setup wizard powered by packaged preset configurations.
- Near real-time visibility into the job discovery pipeline via event feeds.
- A foundational company directory tracking ATS portal URLs and recruiter contacts.
- Strict scoring and tailoring engines that refuse to hallucinate or invent candidate facts.
- A robust Finite State Machine (FSM) tracking the lifecycle of application runs.
- Playwright-powered task workers that capture screenshots and enforce required manual pauses.
- Authorized OAuth integrations for Gmail and Outlook to retrieve verification codes automatically.
- A comprehensive export tool for saving user preferences and configurations locally.

## Ironclad Operating Rules

When modifying or extending ApplyForge, you must adhere to these non-negotiable invariants:

1. **The Master Profile is Supreme**: Generated resumes or cover letters must never contradict or fabricate information not present in the canonical profile.
2. **Fact-Locked Tailoring**: AI optimization is restricted to rephrasing, reordering, and summarizing. It cannot invent new jobs, skills, or metrics.
3. **Strategy Governs Automation**: The user's predefined role strategy acts as the absolute threshold for deciding if a job is eligible for automated submission.
4. **Templates are Just Views**: Resume themes are presentation layers; they do not dictate or store the underlying factual data.
5. **Auditable Execution**: Every automated application run must persist enough telemetry (logs, screenshots) to reconstruct exactly what the browser did prior to failure or completion.
6. **Protect Sensitive Operations**: Email tokens, passwords, and answers to legally sensitive questions must be heavily guarded, masked in logs, and subject to manual user approval.

## Navigational Landmarks

### Resume Processing & Document Generation
- Core extraction: `apps/api/app/services/resume_parser.py`
- Theme and template management: `apps/api/app/services/resume_themes.py` & `apps/api/app/services/resume_templates.py`
- Frontend UI: `apps/web/app/resume/page.tsx`

### Discovery, Enrichment, & Scoring
- Scrape orchestration: `apps/api/app/services/role_ingestion.py`
- Worker task queuing: `apps/api/app/services/job_dispatch.py` & `apps/api/app/services/job_enrichment.py`
- Fit analysis logic: `apps/api/app/services/scoring.py`
- Frontend UI: `apps/web/app/jobs/page.tsx`

### Execution & State Management
- Job execution logic: `apps/api/app/services/application_packets.py` & `apps/worker/app/playwright_runner.py`
- Run FSM logic: `apps/api/app/services/application_fsm.py` & `apps/worker/app/run_fsm.py`
- Worker persistence: `apps/worker/app/persistence.py`

### Configuration & Diagnostics
- Inbox connections: `apps/api/app/services/inbox.py`
- Settings UI: `apps/web/components/forms/settings-form.tsx`
- Run review UI: `apps/web/app/runs/[id]/page.tsx`

## Utilizing Local Agents & Skills

If you are leveraging the automated workflow tools included in this repository, begin your investigation with the localized skill documents:

- For business rules and tailoring constraints: `../.agents/skills/applyforge-product/SKILL.md`
- For worker telemetry, FSM rules, and artifact handling: `../.agents/skills/applyforge-ops/SKILL.md`
- To review agent roles: `../.codex/config.toml`

## Standard Quality Gates

Before merging major changes, ensure you validate the system state:

1. **Python Compilation**: `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. **API Tests**: `PYTHONPATH=/tmp/applyforge-pydeps:apps/api python3 -m pytest apps/api/tests -q`
3. **Worker Tests**: `PYTHONPATH=/tmp/applyforge-pydeps:apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. **Frontend Checks**: In `apps/web`, sequentially run `npm run lint`, `npm run build`, and `npm run typecheck`.

## Ground Truth Reminders

- The worker infrastructure is functional and handles real applications, but field adapter coverage is currently at an MVP stage and handles primarily standard input types.
- The ability to successfully export a resume PDF is prioritized over strict allegiance to RenderCV; fallback mechanisms are essential and must remain active.
- OAuth implementation is code-complete, but requires valid, live provider credentials configured in your `.env` to test effectively.
- Always update documentation to reflect the system's *actual* capabilities today, rather than documenting future intentions as present realities.
