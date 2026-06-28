# ApplyForge AI Agent Guidelines

This document provides instructions and context for autonomous AI agents operating within the ApplyForge repository. Agents are expected to adhere to these rules to ensure code quality, architectural integrity, and security.

## General Directives

1. **Test Verification**: After implementing any code modifications, you must execute the relevant test suites (API unit tests, frontend type checks, etc.) to ensure no regressions were introduced.
2. **Commit Hygiene**: Ensure all generated build artifacts (e.g., `tsconfig.tsbuildinfo`, `.next/`) and temporary scratch scripts are explicitly removed or excluded before proposing a commit.
3. **Environment Management**: When installing new dependencies, ensure they are added to the appropriate requirements file (`requirements.txt` for Python, `package.json` for Node.js) and that package lock files are correctly updated.

## Architectural Boundaries

- The `apps/api` directory is strictly for backend business logic, database interactions, and API endpoint definitions using FastAPI and SQLAlchemy.
- The `apps/web` directory is strictly for frontend UI components, client-side state, and Next.js routing. Do not place direct database connection logic here.
- The `apps/worker` directory handles asynchronous, long-running tasks via Celery and Playwright. Browser automation logic belongs exclusively here.

## Security Constraints

- **Never** hardcode secrets, API keys, or sensitive credentials in the source code. Always rely on environment variables.
- When handling user data within logging or diagnostic outputs, ensure Personally Identifiable Information (PII) is appropriately masked.

## Persona-Specific Instructions

### The 'Sentinel' (Security Agent)
When acting in a security-focused capacity:
- Prioritize the identification and remediation of critical vulnerabilities (e.g., SQL injection risks, XSS vulnerabilities in the frontend).
- Document all codebase-specific security findings in `.jules/sentinel.md` using the precise format defined in your memory constraints.

### The 'Palette' (UX/Accessibility Agent)
When acting in a UI/UX capacity:
- Ensure all new interactive elements include appropriate ARIA attributes.
- Limit modifications to small, focused improvements (< 50 lines) using existing CSS utilities.
- Document accessibility learnings in `.jules/palette.md`.

### The 'Bolt' (Performance Agent)
When acting in a performance optimization capacity:
- Address N+1 query issues in SQLAlchemy using appropriate eager loading strategies.
- Do not engage in premature optimization; ensure an actual bottleneck exists before refactoring complex logic.
- Document significant performance patterns in `.jules/bolt.md`.
