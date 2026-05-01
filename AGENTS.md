# 🤖 ApplyForge Agent Guide

This repository utilizes a lightweight, ECC-style workflow tailored to the agent and skill configurations explicitly defined within this codebase. This guide outlines how AI agents and human operators should interact with the project.

## 🎯 Core Principles

To maintain a healthy, predictable, and robust codebase, all agents must adhere to the following principles:

1. **Plan Before Executing:** Always architect and plan cross-module changes before writing code.
2. **Uphold Truth (No Hallucinations):** ApplyForge must remain strictly truth-constrained. *Never* invent or fabricate resume facts, work histories, or application answers.
3. **Capture Operational Evidence:** Always ensure automation runs persist detailed operational evidence (logs, screenshots, step statuses).
4. **Prioritize Focused Tests:** Write and run localized, focused tests before attempting broad or sweeping refactors.
5. **Maintain Legibility:** Keep the repository understandable. Strive for small files, explicit domain boundaries, and clear, descriptive failure states.

---

## 🎭 Local Agent Roles

Project-local agent roles are defined in [`.codex/agents`](./.codex/agents). These roles define specific operational focuses:

- **`product-planner`**: Focuses on product decomposition, workflow design, and roadmap shaping.
- **`ops-investigator`**: Specializes in diagnosing worker behavior, queue management, and automation troubleshooting.
- **`explorer`**: Dedicated to read-only repository investigation and context gathering.
- **`reviewer`**: Responsible for code correctness, maintainability audits, and regression reviews.
- **`docs-researcher`**: Ensures documentation cross-checking and API/reference validation.

*Usage:* Utilize these roles when the development harness supports multi-agent execution. If multi-agent execution is unavailable, a single agent should logically divide its workflow to respect these distinct concerns.

---

## 🛠️ Local Skills

Project-local skills are defined in [`.agents/skills`](./.agents/skills). These provide ApplyForge-specific domain knowledge:

- **`applyforge-product`**: Deep context on resume intelligence, job scoring algorithms, tailoring constraints, and application workflow product rules.
- **`applyforge-ops`**: Expertise in automation logging, OTP handling flows, diagnostics, worker execution behavior, and run evidence persistence.

Additionally, standard repository-level Codex skills remain highly relevant:
- `tdd-workflow`
- `security-review`
- `api-design`
- `backend-patterns`
- `frontend-patterns`
- `e2e-testing`
- `verification-loop`

---

## 🛡️ Product Invariants

These rules are non-negotiable and dictate the absolute boundaries of the system's behavior:

- **The Canonical Profile is Absolute:** The user's canonical candidate profile is the *only* trusted source of factual information.
- **Strictly Fact-Locked Tailoring:** Resume tailoring algorithms may emphasize, summarize, or reorder facts, but they may *never* invent them.
- **Approval Gates for the Unknown:** Unknown, ambiguous, or risky application questions (e.g., salary expectations) must trigger mandatory manual review gates.
- **Secure OTP Handling:** One-Time Passwords (OTPs) must remain masked in all logs and strictly scoped to the user's active application flow.
- **Resilient Export Paths:** ATS-safe resume export paths must remain highly available, serving as a reliable fallback even when richer, complex renderers fail.
- **Role-Driven Strategy:** A user's defined 'Role Strategy' acts as the controlling input for job discovery, scoring context, and auto-apply eligibility.

---

## ⚙️ Engineering Workflow

Follow this structured workflow for all development tasks:

1. **Inspect:** Examine the relevant code paths and current state before proposing changes.
2. **Test First:** Write or extend test coverage for the specific behavior being introduced or modified.
3. **Iterate Small:** Implement the smallest coherent slice of functionality.
4. **Review:** Audit the change for security vulnerabilities and regression risks.
5. **Verify:** Run localized verification (linters, typechecks, unit tests) before widening the scope of the PR.
6. **Document:** Always update relevant documentation when altering product or operational behavior.

---

## 🔒 Security Rules

Security is a primary concern. The following rules must never be violated:

- **No Hardcoded Secrets:** Never commit hardcoded API keys, tokens, passwords, or provider credentials.
- **Validate at Boundaries:** All external inputs must be validated at system boundaries.
- **Encrypt at Rest:** OAuth tokens and inbox credentials must be stored encrypted at rest and thoroughly sanitized in API responses.
- **Respect Boundaries:** Do *not* implement CAPTCHA bypasses, anti-bot circumvention mechanisms, or fake-answer generation features.
- **Protect Privacy:** Ensure sensitive details (PII, tokens, prompts, error payloads) are never leaked in logs, screenshots, or error messages.

---

## ✅ Verification Expectations

Before completing any task, ensure the appropriate verification loops have been executed successfully:

**Backend Changes (`apps/api`):**
- Execute the full API test suite (`make api-test`).
- Ensure all route and service coverage remains green.

**Worker Changes (`apps/worker`):**
- Add focused unit tests for pure helper logic, especially when the Playwright browser runtime cannot be invoked locally.
- Confirm that durable run-state behavior and screenshot/evidence handling remain intact.

**Web Changes (`apps/web`):**
- Run Next.js linting: `pnpm lint` (or `npm run lint`)
- Verify the build: `pnpm build` (or `npm run build`)
- Execute TypeScript checks: `pnpm typecheck` (or `npm run typecheck`)

---

## 🗺️ Architecture Boundaries

Understand the primary domains of the monorepo:

- **`apps/api`**: FastAPI application, Pydantic schemas, SQLAlchemy ORM, domain services, auth, and data persistence.
- **`apps/web`**: Next.js App Router frontend serving the operator UI and core product surfaces.
- **`apps/worker`**: Celery tasks, Playwright browser automation, and data enrichment runners.
- **`packages/prompts`**: Centralized repository for prompt templates and LLM instruction assets.
- **`docs`**: The source of truth for product requirements, architecture decisions, context, roadmaps, and ideas.

---

## 📌 ApplyForge-Specific Operational Notes

- **"Near-Realtime" Definition:** The job feed operates on durable event histories combined with polling mechanisms. It is *not* a guaranteed live, streaming WebSocket connection.
- **Separation of Concerns:** Job discovery and job enrichment are explicitly separate, independent stages in the pipeline.
- **Fail Loudly:** Automation pipelines should fail loudly and provide useful context, rather than failing silently.
- **Diagnostic Clarity:** Admin and diagnostic UI surfaces must clearly explain *why* a run paused, failed, or requires human intervention.
