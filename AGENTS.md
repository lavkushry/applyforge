# ApplyForge Agent Guide

This repository uses a lightweight ECC-style workflow adapted to the agent and skill configuration that actually exists in this codebase.

## Core Principles

1. Plan before editing when the change spans multiple modules.
2. Keep ApplyForge truth-constrained: never invent resume facts or application answers.
3. Persist operational evidence for automation runs.
4. Prefer tests with focused coverage before broad refactors.
5. Keep the repo understandable: small files, explicit boundaries, clear failure states.

## Local Agent Roles

Project-local agent roles live in [`.codex/agents`](.codex/agents):

- `product-planner`
  - Product decomposition, workflow design, roadmap shaping.
- `ops-investigator`
  - Worker behavior, diagnostics, queue/automation troubleshooting.
- `explorer`
  - Read-only repo investigation and context gathering.
- `reviewer`
  - Correctness, maintainability, and regression review.
- `docs-researcher`
  - Documentation cross-checking and API/reference validation.

Use them when the harness supports multi-agent execution. If multi-agent is unavailable, follow the same division of concerns locally.

## Local Skills

Project-local skills live in [`.agents/skills`](.agents/skills):

- `applyforge-product`
  - Resume intelligence, job scoring, tailoring, and application workflow product rules.
- `applyforge-ops`
  - Automation logging, OTP handling, diagnostics, worker behavior, and run evidence.

Repo-level Codex skills also apply when relevant, especially:

- `tdd-workflow`
- `security-review`
- `api-design`
- `backend-patterns`
- `frontend-patterns`
- `e2e-testing`
- `verification-loop`

## Product Invariants

- The canonical candidate profile is the only trusted fact source.
- Resume tailoring may emphasize or reorder facts, but may not invent them.
- Unknown or risky application questions must become review gates.
- OTP handling must stay masked in logs and scoped to the user’s own application flow.
- ATS-safe resume paths must remain available even when richer renderers fail.
- Role strategy controls discovery, scoring context, and auto-apply eligibility.

## Engineering Workflow

1. Inspect relevant code paths first.
2. Write or extend tests for the behavior being changed.
3. Implement the smallest coherent slice.
4. Review for security and regression risk.
5. Run focused verification before widening scope.
6. Update docs when product or operational behavior changes.

## Security Rules

- Never hardcode secrets, tokens, passwords, or provider credentials.
- Validate all external inputs at system boundaries.
- Keep OAuth and inbox tokens encrypted at rest and sanitized in responses.
- Do not add CAPTCHA bypass, anti-bot circumvention, or fake-answer generation.
- Avoid leaking sensitive details in logs, prompts, screenshots, or error payloads.

## Verification Expectations

Backend changes:

- Run the API test suite when API or service behavior changes.
- Keep route and service coverage green.

Worker changes:

- Add focused unit tests for pure helper logic when browser runtime is not available.
- Preserve durable run-state behavior and screenshot/file evidence handling.

Web changes:

- Run `npm run lint`
- Run `npm run build`
- Run `npm run typecheck`

## Architecture Boundaries

- `apps/api`
  - FastAPI API, schemas, domain services, auth, persistence.
- `apps/web`
  - Next.js operator UI and product surface.
- `apps/worker`
  - Celery tasks, Playwright automation, enrichment runners.
- `packages/prompts`
  - Prompt templates and model-facing instruction assets.
- `docs`
  - Product, architecture, context, roadmap, and idea documents.

## ApplyForge-Specific Notes

- Near-realtime job feed means durable event history plus polling, not guaranteed live streaming.
- Discovery and enrichment are separate stages.
- Automation should fail loudly and usefully, not silently.
- Admin/diagnostic surfaces should explain why a run paused, failed, or requires human intervention.
