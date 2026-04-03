# Agent Interaction Guidelines for ApplyForge

This repository implements a targeted ECC (Engineering, Context, and Coordination) workflow. It is specifically tuned for the local agent and skill structures present within this monorepo.

## Guiding Directives

1. **Architect First:** Always map out cross-module implications and write a plan before modifying code.
2. **Uphold Truth:** ApplyForge operates strictly on reality. Under no circumstances should an agent invent, guess, or hallucinate resume details or application responses.
3. **Capture the Trail:** Ensure that every automated task leaves behind durable operational evidence (e.g., logs, screenshots, metrics).
4. **Targeted Verification:** Prioritize writing focused, localized tests over large-scale, sweeping refactors.
5. **Simplicity and Clarity:** Maintain a legible codebase. Ensure files are concise, domain boundaries are respected, and error states are clearly communicated.

## Defined Agent Personas

The project leverages specialized agent configurations located in [`.codex/agents`](.codex/agents):

- **`product-planner`**: Focuses on breaking down features, designing workflows, and shaping the product roadmap.
- **`ops-investigator`**: Specializes in diagnosing worker behavior, inspecting automation queues, and troubleshooting runtime anomalies.
- **`explorer`**: A read-only agent dedicated to navigating the codebase and synthesizing context without altering state.
- **`reviewer`**: Evaluates proposed changes against architectural standards, checking for regressions and maintainability.
- **`docs-researcher`**: Validates that documentation accurately reflects current code behavior and API signatures.

When working in a multi-agent framework, route tasks to the appropriate persona. If operating locally, internalize these divisions of concern to ensure rigorous review.

## Project-Specific Skills

Reusable knowledge blocks are maintained in [`.agents/skills`](.agents/skills):

- **`applyforge-product`**: Governs the rules for resume parsing, job scoring logic, document tailoring constraints, and application workflow integrity.
- **`applyforge-ops`**: Details the standards for automation logging, sensitive OTP management, diagnostics collection, and worker state persistence.

You should also apply standard Codex capabilities, including:
`tdd-workflow`, `security-review`, `api-design`, `backend-patterns`, `frontend-patterns`, `e2e-testing`, and `verification-loop`.

## Ironclad Product Rules

- **The Canonical Profile is Absolute**: The candidate’s core profile is the single source of truth.
- **No Hallucinations**: Tailoring operations may summarize or restructure existing text, but they must never introduce new facts.
- **Fail Closed on Ambiguity**: Any unknown, undefined, or high-risk application question must immediately halt automation and require human review.
- **Data Privacy**: One-Time Passwords (OTPs) and related tokens must be masked in all logs and strictly isolated to the specific user's application context.
- **Export Continuity**: The system must always provide a safe, text-extractable ATS resume export, even if advanced rendering engines fail.
- **Strategy Dictates Action**: The configured role strategy is the ultimate authority over discovery scopes, match scoring, and auto-application eligibility.

## Standard Development Loop

1. **Investigate**: Thoroughly explore the relevant code and documentation.
2. **Test First**: Write or update tests that cover the intended behavior change.
3. **Iterate Small**: Implement the smallest possible functional slice.
4. **Audit**: Review the changes for security implications and unintended side effects.
5. **Verify Locally**: Execute targeted validations before proceeding to broader tests.
6. **Document**: Synchronize documentation with any modifications to product functionality or operational procedures.

## Security Posture

- **No Hardcoded Secrets**: Credentials, API keys, and tokens must never be committed to the repository.
- **Strict Boundaries**: Validate and sanitize all inputs at every system boundary.
- **Encrypted at Rest**: OAuth tokens and inbox credentials must be encrypted in the database and masked when returned via APIs.
- **Respect Employer Controls**: Never implement code designed to bypass CAPTCHAs, spoof anti-bot mechanisms, or generate fake responses.
- **Clean Logging**: Prevent sensitive data (prompts, personal information, screenshots) from leaking into plaintext application logs.

## Testing Standards

**Backend/API**:
- Ensure the API test suite passes after any modifications to route logic, schemas, or service layers.
- Maintain high coverage for critical paths like scoring and application packets.

**Worker/Celery**:
- Develop isolated unit tests for internal helper functions that do not require the Playwright runtime.
- Verify that task state transitions and artifact (screenshot/file) captures remain robust.

**Frontend/Web**:
- Validate changes via `npm run lint`.
- Ensure production readiness via `npm run build`.
- Enforce strict type safety via `npm run typecheck`.

## Subsystem Boundaries

- **`apps/api`**: Owns the FastAPI application, Pydantic schemas, core domain logic, authentication, and database interactions.
- **`apps/web`**: Owns the Next.js frontend, user experience, and operator dashboards.
- **`apps/worker`**: Owns Celery task processing, Playwright browser interactions, and external data enrichment.
- **`packages/prompts`**: Owns all Large Language Model instructions, prompt templates, and routing logic.
- **`docs`**: Owns architectural records, system guides, and strategic roadmap documents.

## Operational Context

- **Eventual Consistency**: The job feed relies on scheduled polling and durable event logs rather than immediate WebSocket streaming.
- **Separation of Concerns**: Job discovery and subsequent data enrichment are two distinct operational phases.
- **Loud Failures**: Automated tasks are designed to fail transparently rather than silently ignoring errors.
- **Diagnostic Clarity**: Administrative tools and logs must always clearly articulate *why* a process paused, failed, or requires operator intervention.
