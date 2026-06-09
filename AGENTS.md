# ApplyForge Artificial Intelligence Agent Guide

This document outlines the lightweight workflow and configuration framework tailored for AI agents operating within the ApplyForge repository.

## Fundamental Principles

1. **Strategic Planning:** When changes span multiple modules, agents must draft a comprehensive plan before executing edits.
2. **Strict Fact-Checking:** Agents must ensure ApplyForge never fabricates resume details or hallucinates application responses.
3. **Auditable Operations:** Agents must preserve clear, durable evidence for all automated runs and system processes.
4. **Targeted Verification:** Prioritize focused, isolated tests over sweeping refactors when modifying core logic.
5. **Architectural Clarity:** Maintain repository legibility by enforcing small file sizes, strict module boundaries, and explicit error states.

## Resident Agent Profiles

Project-specific agent configurations are located in [`.codex/agents`](.codex/agents):

- `product-planner`
  - Responsible for feature decomposition, workflow mapping, and shaping the product roadmap.
- `ops-investigator`
  - Specialized in troubleshooting worker behaviors, queue blockages, and automation pipeline failures.
- `explorer`
  - A read-only agent dedicated to investigating the repository and gathering context without making modifications.
- `reviewer`
  - Tasked with auditing code for correctness, structural maintainability, and potential regressions.
- `docs-researcher`
  - Focused on cross-referencing documentation, validating API specifications, and maintaining technical references.

Engage these specialized profiles when the operating environment supports multi-agent execution. If constrained to a single agent, strictly emulate this division of labor during different phases of the task.

## Defined Skill Sets

Domain-specific operational skills are maintained in [`.agents/skills`](.agents/skills):

- `applyforge-product`
  - Contains the business logic rules governing resume parsing, job scoring heuristics, document tailoring, and the application execution workflow.
- `applyforge-ops`
  - Dictates the protocols for automation logging, secure OTP handling, diagnostic procedures, worker lifecycle management, and evidence retention.

Additionally, standard Codex repository skills should be applied where relevant, including:
- `tdd-workflow`
- `security-review`
- `api-design`
- `backend-patterns`
- `frontend-patterns`
- `e2e-testing`
- `verification-loop`

## Immutable Product Directives

- The user's canonical profile serves as the sole authoritative source of truth.
- While tailoring a resume may emphasize specific experiences or reorder bullet points, it must never invent new facts.
- Any encountered application questions that are unknown or carry significant risk must automatically trigger a manual user review gate.
- OTP retrieval mechanisms must be strictly scoped to the user's active application session, and the actual codes must remain masked in all logs.
- Reliable, ATS-compliant resume generation pathways must remain operational even if advanced formatting engines fail.
- The user's defined "Role strategy" serves as the primary controller governing job discovery, scoring metrics, and auto-apply eligibility.

## Standard Engineering Protocol

1. Analyze and understand the relevant code paths prior to modification.
2. Author or expand tests specifically targeting the intended behavior change.
3. Implement the solution in the smallest, most coherent increment possible.
4. Conduct a rigorous review focusing on security vulnerabilities and regression risks.
5. Execute targeted verification (e.g., specific unit tests) before expanding the scope of the change.
6. Synchronize documentation whenever product functionality or operational procedures are altered.

## Security Mandates

- Hardcoding secrets, authentication tokens, passwords, or external provider credentials is strictly prohibited.
- All external inputs must be validated at the system boundaries before processing.
- OAuth credentials and inbox access tokens must be encrypted at rest and sanitized before being included in any API response.
- Do not implement systems designed to bypass CAPTCHAs, circumvent anti-bot measures, or generate fake responses to security questions.
- Ensure sensitive user details, raw prompts, application screenshots, and error tracebacks do not leak personally identifiable information (PII) into the logging infrastructure.

## Required Verification Steps

**Backend Modifications:**
- Execute the full API test suite whenever routing or service logic is altered.
- Maintain a green build for all route and service test coverage.

**Worker Modifications:**
- Implement focused unit tests for helper functions and core logic, especially when a full browser runtime environment is unavailable.
- Ensure that the durable logging of run states and the handling of screenshot evidence remain fully intact.

**Frontend (Web) Modifications:**
- Execute `npm run lint`
- Execute `npm run build`
- Execute `npm run typecheck`

## Repository Structure & Boundaries

- `apps/api`
  - Contains the FastAPI backend, data schemas, core domain services, authentication logic, and database interactions.
- `apps/web`
  - Houses the Next.js frontend, providing the operator dashboard and user-facing product surfaces.
- `apps/worker`
  - Manages Celery tasks, Playwright browser automation scripts, and background enrichment processes.
- `packages/prompts`
  - Stores prompt templates and structured instructions designed for Large Language Model (LLM) interactions.
- `docs`
  - The central repository for product specifications, architectural diagrams, contextual guides, roadmaps, and conceptual documents.

## ApplyForge Operational Nuances

- The "near-realtime" job feed relies on durable event history combined with active polling; it is not a guaranteed live, persistent stream.
- Job discovery (finding the posting) and job enrichment (extracting detailed data) are executed as explicitly separate operational stages.
- Automated processes must fail loudly and provide actionable diagnostics, rather than failing silently.
- Administrative and diagnostic interfaces must clearly articulate the reasoning behind a run pausing, failing, or requesting human intervention.
