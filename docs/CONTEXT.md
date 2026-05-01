# ApplyForge Context Guide

This document is designed to rapidly orient new engineers (and AI agents) to the ApplyForge codebase, dramatically reducing the cost of rediscovery in future development sessions.

---

## 🚀 What ApplyForge Is

ApplyForge is a comprehensive job-hunt operating system built around five interconnected, continuous loops:

1. **Candidate Intelligence:** Maintaining a canonical profile and extracting resume data.
2. **Targeted Discovery:** Role-driven job scraping, normalization, and deep enrichment.
3. **Transparent Evaluation:** Algorithmic job scoring and fact-locked resume tailoring.
4. **Guarded Automation:** Browser-assisted application execution with strict pause gates.
5. **Operator Oversight:** Comprehensive diagnostics, OTP retrieval, and manual review queues.

---

## 📦 Current Product Shape

The repository is highly functional and currently supports the following capabilities:

- **Identity:** Cookie-backed authentication and full canonical profile CRUD.
- **Documents:** Resume upload/parsing, ATS-safe light theme catalog, packaged Markdown/LaTeX starter templates, and RenderCV-compatible generation (with an internal PDF fallback).
- **Discovery:** Role registry, source subscriptions, packaged discovery presets, setup wizard bootstrapping, and a near-realtime feed powered by background ingestion.
- **Corporate Graph:** User-scoped company directory records mapping canonical portals and recruiter contacts.
- **Intelligence:** Explicit pipelining from discovery → queued enrichment → transparent scoring.
- **Automation:** Preflight application packets, durable application runs, step logs, formal FSM state transitions, and browser-driven execution via Playwright.
- **Integrations:** Gmail and Outlook OAuth readiness, including OTP retrieval mechanisms.
- **Portability:** Exportable automation preference profiles available directly from the Settings UI.

---

## 🛡️ Core System Invariants

These rules are the foundation of ApplyForge's integrity and must be preserved during all modifications:

1. **The Canonical Profile is Absolute:** The user's parsed/edited profile is the *only* authoritative source of facts.
2. **Zero Hallucination Tolerance:** Document generation and tailoring engines may optimize phrasing and order, but they must *never* fabricate or invent facts.
3. **Role Strategy is King:** The user's defined Role Strategy acts as the sole controlling input for job discovery, scoring algorithms, and auto-apply eligibility.
4. **Themes are Presentation Only:** Resume themes and templates are strictly presentation layers. They must never become a secondary source of truth for user data.
5. **Durable Automation Evidence:** The worker runtime must ensure application automation remains fully inspectable (via logs and screenshots) even after partial or total failures.
6. **Masked Sensitivity:** Sensitive tokens, OTP codes, and risky application answers must always be masked in logs or hidden behind explicit manual approval gates.

---

## 📍 Best Entry Points By Task

If you need to make changes, start your investigation at these core files:

### Resumes, Templates, & Export
- **Parser:** `apps/api/app/services/resume_parser.py`
- **Themes/Templates:** `apps/api/app/services/resume_themes.py`, `apps/api/app/services/resume_templates.py`
- **Files:** `apps/api/app/services/files.py`
- **UI:** `apps/web/app/resume/page.tsx`

### Jobs, Roles, & Scoring
- **Ingestion/Enrichment:** `apps/api/app/services/role_ingestion.py`, `apps/api/app/services/job_dispatch.py`, `apps/api/app/services/job_enrichment.py`
- **Companies:** `apps/api/app/services/company_directory.py`, `apps/api/app/api/routes/companies.py`
- **Scoring Logic:** `apps/api/app/services/scoring.py`
- **Routes:** `apps/api/app/api/routes/roles.py`, `apps/api/app/api/routes/jobs.py`

### Automation, Packets, & FSM (Backend/Worker)
- **API Services:** `apps/api/app/services/application_packets.py`, `apps/api/app/services/application_fsm.py`, `apps/api/app/services/user_preferences.py`
- **API Routes:** `apps/api/app/api/routes/applications.py`, `apps/api/app/api/routes/application_runs.py`
- **Worker Logic:** `apps/worker/app/playwright_runner.py`, `apps/worker/app/persistence.py`, `apps/worker/app/run_fsm.py`

### Settings, OTP, & Operator UX
- **Inbox/OTP:** `apps/api/app/services/inbox.py`, `apps/api/app/api/routes/inbox.py`
- **Settings UI:** `apps/web/components/forms/settings-form.tsx`
- **Run Tracking UI:** `apps/web/app/applications/page.tsx`, `apps/web/app/runs/[id]/page.tsx`

---

## 🤖 Project-Local Context Helpers

Before undertaking broad architectural exploration, consult the project-local AI agent skill files. They contain critical, ApplyForge-specific context:

- **Product/Domain Rules:** [`.agents/skills/applyforge-product/SKILL.md`](./.agents/skills/applyforge-product/SKILL.md)
- **Operational Rules:** [`.agents/skills/applyforge-ops/SKILL.md`](./.agents/skills/applyforge-ops/SKILL.md)
- **Agent Registry:** [`.codex/config.toml`](./.codex/config.toml)

---

## ✅ Current Verification Baseline

When implementing nontrivial changes, you are expected to run the following checks from the repository root to ensure baseline stability:

1. **Compile Python:**
   `python3 -m compileall apps/api/app apps/api/tests apps/worker/app apps/worker/tests`
2. **Run API Tests:**
   `PYTHONPATH=/tmp/applyforge-pydeps:$(pwd)/apps/api python3 -m pytest apps/api/tests -q`
3. **Run Worker Tests:**
   `PYTHONPATH=/tmp/applyforge-pydeps:$(pwd)/apps/worker DATABASE_URL=sqlite+pysqlite:///:memory: REDIS_URL=redis://localhost:6379/0 python3 -m pytest apps/worker/tests -q`
4. **Lint Web Frontend:**
   `cd apps/web && pnpm lint`
5. **Build Web Frontend:**
   `cd apps/web && pnpm build`
6. **Typecheck Web Frontend:**
   `cd apps/web && pnpm typecheck` *(Run this after the build command, as TS config relies on generated `.next/types`.)*

---

## 💡 Current Reality Checks (Caveats)

Please be aware of the following realities in the current implementation:

- **Worker Coverage:** The Celery/Playwright worker path is fully operational for enrichment and application execution, but it currently provides MVP-level coverage for the massive variety of HTML input fields found in the wild.
- **Export Philosophy:** Continuity of the resume export process is more important than achieving renderer purity. If the primary RenderCV generation fails, the internal fallback *must* succeed.
- **OAuth Testing:** While the OAuth code paths are implemented, comprehensive end-to-end verification against live provider credentials is still required.
- **Documentation Discipline:** Documentation must describe *current* system behavior, not future aspirations or promises. Maintain this strict discipline.